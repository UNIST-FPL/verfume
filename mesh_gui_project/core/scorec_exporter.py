"""
SCOREC PUMI format exporters.

This module provides writers for SCOREC PUMI mesh formats:
- .dmg: ASCII discrete geometric model
- .smb: Binary mesh data structure (version 6)
"""
import numpy as np
from typing import Dict, List, Tuple, Any, Set
import logging
import struct
from mesh_gui_project.core.scorec_utils import TopologyBuilder, EntityClassifier

logger = logging.getLogger(__name__)


class BoundaryExtractor:
    """Extract discrete geometric model from 2D triangular mesh."""

    def __init__(self):
        """Initialize BoundaryExtractor."""
        self.topology = TopologyBuilder()
        self.classifier = EntityClassifier()
        self.logger = logging.getLogger(__name__)

    def _classify_mesh_edges(
        self,
        elements: np.ndarray,
        boundary_edges: Set[Tuple[int, int]],
        model_edges: List[Tuple[int, int, int]],
        edge_chains: List[List[int]]
    ) -> Dict[int, Tuple[int, int]]:
        """
        Classify mesh edges to geometric model entities.

        CRITICAL: Edge classification MUST respect the 2-manifold property:
        - Edges with 1 adjacent triangle → boundary edge (dim=1)
        - Edges with 2 adjacent triangles → interior edge (dim=2)

        This ensures mesh->verify() passes in PUMI.

        Args:
            elements: Triangle connectivity
            boundary_edges: Set of boundary edge tuples (v1, v2)
            model_edges: List of (tag, v1, v2) for model edges
            edge_chains: List of edge chains (vertex sequences)

        Returns:
            Dict mapping mesh edge index -> (dim, tag)
            where dim=1 for model edge, dim=2 for model face
        """
        # Build a map from mesh vertex pair to model edge tag
        # CRITICAL: Map ALL edges in each chain, not just endpoints!
        model_edge_map = {}
        for tag, chain in enumerate(edge_chains):
            # Map every consecutive pair of vertices in the chain to this model edge tag
            for i in range(len(chain) - 1):
                v1, v2 = chain[i], chain[i + 1]
                edge_key = (min(v1, v2), max(v1, v2))
                model_edge_map[edge_key] = tag

        # Generate edges from triangles AND count triangle adjacencies
        edge_dict = {}
        edges_list = []
        edge_triangle_count = []  # Track how many triangles each edge belongs to

        for triangle in elements:
            edge_vertices = [
                (triangle[0], triangle[1]),
                (triangle[1], triangle[2]),
                (triangle[2], triangle[0])
            ]

            for v1, v2 in edge_vertices:
                edge_key = (min(v1, v2), max(v1, v2))
                if edge_key not in edge_dict:
                    edge_idx = len(edges_list)
                    edge_dict[edge_key] = edge_idx
                    edges_list.append(edge_key)
                    edge_triangle_count.append(0)

                # Increment triangle count for this edge
                edge_idx = edge_dict[edge_key]
                edge_triangle_count[edge_idx] += 1

        # Classify each mesh edge based on triangle adjacency count
        edge_class = {}

        for edge_idx, (v1, v2) in enumerate(edges_list):
            edge_key = (min(v1, v2), max(v1, v2))
            tri_count = edge_triangle_count[edge_idx]

            # CRITICAL: Use triangle adjacency count to determine classification
            if tri_count == 1:
                # Edge with 1 triangle MUST be boundary (dim=1)
                # Look up the corresponding model edge
                if edge_key in model_edge_map:
                    model_tag = model_edge_map[edge_key]
                    edge_class[edge_idx] = (1, model_tag)
                else:
                    # Edge not in model_edge_map - this should NOT happen now
                    # that we map all chain edges. If it does, it indicates a mesh
                    # with topology gaps or non-manifold edges.
                    self.logger.error(f"Edge {edge_key} has 1 triangle but not found in any edge chain - possible mesh topology error")
                    # Classify as boundary edge 0 to avoid crash
                    edge_class[edge_idx] = (1, 0)

            elif tri_count == 2:
                # Edge with 2 triangles - could be boundary or interior
                # Check if it's a geometric boundary
                is_boundary = (v1, v2) in boundary_edges or (v2, v1) in boundary_edges

                if is_boundary:
                    # Geometric boundary edge
                    if edge_key in model_edge_map:
                        model_tag = model_edge_map[edge_key]
                        edge_class[edge_idx] = (1, model_tag)
                    else:
                        # Shouldn't happen, default to edge 0
                        edge_class[edge_idx] = (1, 0)
                else:
                    # Interior edge - classify to model face (dimension 2)
                    edge_class[edge_idx] = (2, 0)

            else:
                # Edge with >2 triangles - non-manifold!
                self.logger.error(f"Edge {edge_key} has {tri_count} triangles - non-manifold mesh!")
                # Classify as boundary to avoid verify() crash
                edge_class[edge_idx] = (1, 0)

        return edge_class

    def extract_model(
        self,
        vertices: np.ndarray,
        elements: np.ndarray,
        angle_threshold: float = 30.0
    ) -> Tuple[Dict[str, Any], Dict[str, Dict]]:
        """
        Extract discrete geometric model from mesh.

        Args:
            vertices: (N, 2) vertex coordinates
            elements: (E, 3) triangle connectivity
            angle_threshold: Angle threshold for corner detection

        Returns:
            Tuple (model_entities, classification):
            - model_entities: Dict for DMG writer
            - classification: Dict for SMB writer
        """
        # Step 1: Build topology
        edge_to_triangles = self.topology.build_edge_to_triangles_map(elements)
        boundary_edges = self.topology.find_boundary_edges(edge_to_triangles)
        edge_chains = self.topology.build_edge_chains(
            boundary_edges, vertices, angle_threshold
        )

        # Step 2: Create model entities
        model_vertices = []  # Corner vertices
        model_edges = []     # Edge chains
        model_faces = []     # Single face for 2D domain

        # Find corner vertices (chain endpoints)
        corner_vertices = set()
        for chain in edge_chains:
            corner_vertices.add(chain[0])
            corner_vertices.add(chain[-1])

        # Create model vertices from corners
        vertex_to_tag = {}
        for tag, v_idx in enumerate(sorted(corner_vertices)):
            x, y = vertices[v_idx]
            model_vertices.append((tag, x, y, 0.0))
            vertex_to_tag[v_idx] = tag

        # Create model edges from edge chains
        for tag, chain in enumerate(edge_chains):
            v1_tag = vertex_to_tag[chain[0]]
            v2_tag = vertex_to_tag[chain[-1]]
            model_edges.append((tag, v1_tag, v2_tag))

        # Create single model face bounded by all edges
        if edge_chains:
            edge_loop = {
                'edges': list(range(len(model_edges))),
                'directions': [0] * len(model_edges)  # All forward
            }
            model_faces.append((0, [edge_loop]))

        # Compute bounding box
        min_coords = vertices.min(axis=0)
        max_coords = vertices.max(axis=0)
        bbox = (float(min_coords[0]), float(min_coords[1]), 0.0,
                float(max_coords[0]), float(max_coords[1]), 0.0)

        model_entities = {
            'model_vertices': model_vertices,
            'model_edges': model_edges,
            'model_faces': model_faces,
            'model_regions': [],
            'bbox': bbox
        }

        # Step 3: Classify mesh entities
        vertex_class = self.classifier.classify_vertices(
            vertices, boundary_edges, edge_chains, vertex_to_tag
        )

        # Classify mesh edges to model edges (boundary) or model face (interior)
        edge_class = self._classify_mesh_edges(
            elements, boundary_edges, model_edges, edge_chains
        )

        # All triangles classify to the single model face
        triangle_class = {t_idx: (2, 0) for t_idx in range(len(elements))}

        classification = {
            'vertex_class': vertex_class,
            'edge_class': edge_class,
            'triangle_class': triangle_class
        }

        self.logger.info(f"Extracted model: {len(model_vertices)} model vertices, "
                        f"{len(model_edges)} model edges, "
                        f"{len(model_faces)} model faces")

        return model_entities, classification


class DMGWriter:
    """Write SCOREC discrete geometric model (.dmg) in ASCII format."""

    def __init__(self):
        """Initialize DMGWriter."""
        self.logger = logging.getLogger(__name__)

    def write_dmg(self, model_entities: Dict[str, Any], path: str) -> None:
        """
        Write .dmg file.

        Args:
            model_entities: Dictionary with:
                - 'model_vertices': List[(tag, x, y, z)]
                - 'model_edges': List[(tag, v1, v2)]
                - 'model_faces': List[(tag, edge_loops)]
                - 'model_regions': List[(tag, shells)]
                - 'bbox': (min_x, min_y, min_z, max_x, max_y, max_z)
            path: Output file path
        """
        model_vertices = model_entities.get('model_vertices', [])
        model_edges = model_entities.get('model_edges', [])
        model_faces = model_entities.get('model_faces', [])
        model_regions = model_entities.get('model_regions', [])
        bbox = model_entities.get('bbox', (0, 0, 0, 0, 0, 0))

        with open(path, 'w') as f:
            # Header: counts
            f.write(f"{len(model_regions)} {len(model_faces)} "
                    f"{len(model_edges)} {len(model_vertices)}\n")

            # Bounding box
            f.write(f"{bbox[0]} {bbox[1]} {bbox[2]}\n")
            f.write(f"{bbox[3]} {bbox[4]} {bbox[5]}\n")

            # Vertices
            for tag, x, y, z in model_vertices:
                f.write(f"{tag} {x} {y} {z}\n")

            # Edges
            for tag, v1, v2 in model_edges:
                f.write(f"{tag} {v1} {v2}\n")

            # Faces
            for face_data in model_faces:
                if isinstance(face_data, tuple) and len(face_data) == 2:
                    tag, loops = face_data
                    f.write(f"{tag} {len(loops)}\n")

                    for loop in loops:
                        edges = loop.get('edges', [])
                        directions = loop.get('directions', [0] * len(edges))
                        f.write(f"{len(edges)}")
                        for edge_tag, direction in zip(edges, directions):
                            f.write(f" {edge_tag} {direction}")
                        f.write("\n")

            # Regions
            for region_data in model_regions:
                if isinstance(region_data, tuple) and len(region_data) == 2:
                    tag, shells = region_data
                    f.write(f"{tag} {len(shells)}\n")

                    for shell in shells:
                        faces = shell.get('faces', [])
                        directions = shell.get('directions', [0] * len(faces))
                        f.write(f"{len(faces)}")
                        for face_tag, direction in zip(faces, directions):
                            f.write(f" {face_tag} {direction}")
                        f.write("\n")

        self.logger.info(f"Wrote .dmg file: {path} "
                        f"({len(model_vertices)} vertices, "
                        f"{len(model_edges)} edges, "
                        f"{len(model_faces)} faces)")


class SMBWriter:
    """Write SCOREC binary mesh (.smb) format version 6."""

    MAGIC = 0  # PUMI writes magic=0 as unsigned int, not "mds" string
    VERSION = 6

    def __init__(self):
        """Initialize SMBWriter."""
        self.logger = logging.getLogger(__name__)

    def _generate_edges(self, elements: np.ndarray) -> Tuple[np.ndarray, Dict[int, List[int]]]:
        """
        Generate unique edges from triangle connectivity.

        Args:
            elements: (E, 3) triangle connectivity (vertex indices)

        Returns:
            Tuple of:
            - edges: (N_edges, 2) array of edge vertex pairs
            - triangle_edges: Dict mapping triangle_idx -> [edge_idx0, edge_idx1, edge_idx2]
        """
        # Use a dictionary to track unique edges and assign indices
        edge_dict = {}  # (v1, v2) -> edge_idx
        edges_list = []
        triangle_edges = {}

        for tri_idx, triangle in enumerate(elements):
            tri_edge_indices = []

            # Get the 3 edges of this triangle
            # Edge ordering: (v0,v1), (v1,v2), (v2,v0)
            edge_vertices = [
                (triangle[0], triangle[1]),
                (triangle[1], triangle[2]),
                (triangle[2], triangle[0])
            ]

            for v1, v2 in edge_vertices:
                # Normalize edge to canonical form (smaller vertex first)
                edge_key = (min(v1, v2), max(v1, v2))

                if edge_key not in edge_dict:
                    # New edge - assign next index
                    edge_idx = len(edges_list)
                    edge_dict[edge_key] = edge_idx
                    edges_list.append(edge_key)
                else:
                    edge_idx = edge_dict[edge_key]

                tri_edge_indices.append(edge_idx)

            triangle_edges[tri_idx] = tri_edge_indices

        # Convert to numpy array
        edges = np.array(edges_list, dtype=np.uint32)

        return edges, triangle_edges

    def write_smb(
        self,
        vertices: np.ndarray,
        elements: np.ndarray,
        classification: Dict[str, Dict],
        path: str,
        dimension: int = 2
    ) -> None:
        """
        Write .smb binary mesh file.

        Args:
            vertices: (N, 2) vertex coordinates
            elements: (E, 3) triangle connectivity
            classification: Dictionary with:
                - 'vertex_class': {v_idx: (dim, tag)}
                - 'triangle_class': {t_idx: (dim, tag)}
            path: Output file path
            dimension: Mesh dimension (2 for 2D)
        """
        n_vertices = len(vertices)
        n_triangles = len(elements)

        # Generate edges from triangles
        edges, triangle_edges = self._generate_edges(elements)
        n_edges = len(edges)

        with open(path, 'wb') as f:
            # Header: magic (unsigned int 0), version, dimension, partitions
            # IMPORTANT: PUMI uses BIG-ENDIAN (network byte order) for all binary data
            f.write(struct.pack('>IIII', self.MAGIC, self.VERSION, dimension, 1))

            # Entity counts (8 unsigned ints)
            # Order: vertices, edges, triangles, quads, hexes, prisms, pyramids, tets
            f.write(struct.pack('>8I',
                              n_vertices,
                              n_edges,  # Now writing actual edges
                              n_triangles,
                              0,  # quads
                              0,  # hexes
                              0,  # prisms
                              0,  # pyramids
                              0)) # tets

            # Connectivity Section:
            # CRITICAL: PUMI expects connectivity in dimension-1 order
            # - Edges connect to vertices (dimension 0)
            # - Triangles connect to edges (dimension 1), NOT vertices!

            # Edges: each edge has 2 vertices
            for edge in edges:
                f.write(struct.pack('>2I', edge[0], edge[1]))

            # Triangles: each triangle has 3 edges (NOT 3 vertices!)
            for tri_idx in range(n_triangles):
                edge_indices = triangle_edges[tri_idx]
                f.write(struct.pack('>3I', edge_indices[0], edge_indices[1], edge_indices[2]))

            # Coordinates: 3D vertices (extend 2D to 3D)
            for vertex in vertices:
                x, y = vertex
                z = 0.0
                f.write(struct.pack('>3d', x, y, z))

            # Parametric coordinates: 2D (PUMI expects this after 3D coords)
            for vertex in vertices:
                u, v = vertex
                f.write(struct.pack('>2d', u, v))

            # Remotes: empty for serial (non-partitioned) meshes
            # Write np=0 to indicate no remote links
            f.write(struct.pack('>I', 0))

            # Classification: MUST write for ALL 8 SMB entity types in order:
            # 0=vertices, 1=edges, 2=triangles, 3=quads, 4=hexes, 5=prisms, 6=pyramids, 7=tets
            # CRITICAL: For each entity, write in order: tag, dim (NOT dim, tag!)
            # Per PUMI mds_smb.c:272-273: class[2*j] = model_id (tag), class[2*j+1] = model_dim

            vertex_class = classification.get('vertex_class', {})
            edge_class = classification.get('edge_class', {})
            triangle_class = classification.get('triangle_class', {})

            # Type 0: Vertices
            for v_idx in range(n_vertices):
                if v_idx in vertex_class:
                    dim, tag = vertex_class[v_idx]
                else:
                    dim, tag = 2, 0  # Default: classify to face
                f.write(struct.pack('>2I', tag, dim))  # Write tag first, then dim!

            # Type 1: Edges
            for e_idx in range(n_edges):
                if e_idx in edge_class:
                    dim, tag = edge_class[e_idx]
                else:
                    dim, tag = 2, 0  # Default: classify to face
                f.write(struct.pack('>2I', tag, dim))  # Write tag first, then dim!

            # Type 2: Triangles
            for t_idx in range(n_triangles):
                if t_idx in triangle_class:
                    dim, tag = triangle_class[t_idx]
                else:
                    dim, tag = 2, 0  # Default: classify to face
                f.write(struct.pack('>2I', tag, dim))  # Write tag first, then dim!

            # Types 3-7: Quads, Hexes, Prisms, Pyramids, Tets (all count=0)
            # (skip - no entities to write)

            # Tags: write 0 to indicate no tags (n=0)
            f.write(struct.pack('>I', 0))

            # Matches (version >= 4): write empty match data for all 8 entity types
            # For each of the 8 SMB types, write np=0 (no remote matches)
            # SMB types order: vertices, edges, triangles, quads, hexes, prisms, pyramids, tets
            for _ in range(8):  # SMB_TYPES = 8
                f.write(struct.pack('>I', 0))  # np=0 for this type

            # Metadata: write minimal APF metadata
            # Shape name (null-terminated string) - must match PUMI registered names
            # "Linear" corresponds to first-order Lagrange elements (getLagrange(1))
            shape_name = b'Linear\x00'
            f.write(shape_name)

            # Version number (negative to indicate versioned format)
            # Use -1 to indicate version 1
            f.write(struct.pack('>i', -1))  # signed int

            # Number of fields (0 for no fields)
            f.write(struct.pack('>I', 0))

        self.logger.info(f"Wrote .smb file: {path} "
                        f"({n_vertices} vertices, {n_edges} edges, {n_triangles} triangles)")
