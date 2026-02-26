"""
Flux-aligned triangular mesh generation.

This module provides tools to create structured triangular meshes aligned
with flux surfaces, suitable for plasma simulation codes.
"""
import numpy as np
from typing import List, Tuple, Optional
import logging
from mesh_gui_project.core.mesh_quality import MeshQualityAnalyzer

try:
    import gmsh
except ImportError:
    gmsh = None

logger = logging.getLogger(__name__)


class FluxMesher:
    """
    Generate flux-aligned triangular meshes from flux surfaces.

    Creates structured meshes by connecting points on successive flux surfaces
    with triangular elements.
    """

    def __init__(self):
        """Initialize FluxMesher."""
        pass

    def build_structured(
        self,
        surfaces: List[np.ndarray],
        axis_point: Optional[Tuple[float, float]] = None
    ) -> Tuple[np.ndarray, np.ndarray]:
        """
        Build structured triangular mesh from flux surfaces.

        Creates a mesh by connecting points on successive flux surfaces with
        triangular elements. Optionally includes an axis point at the center.

        Algorithm:
        1. If axis_point provided: create triangles from axis to first surface
        2. Between each pair of surfaces: split quads into 2 triangles
        3. Handle cyclic wrapping to close the mesh

        Args:
            surfaces: List of flux surface polylines, each shape (M, 2) with (R, Z)
            axis_point: Optional (R, Z) tuple for magnetic axis point

        Returns:
            Tuple (vertices, elements):
            - vertices: np.ndarray shape (N, 2) - (R, Z) coordinates
            - elements: np.ndarray shape (E, 3) - triangle vertex indices
        """
        if len(surfaces) == 0:
            raise ValueError("At least one surface required")

        vertices_list = []
        elements_list = []

        # Add axis point if provided
        vertex_offset = 0
        if axis_point is not None:
            vertices_list.append([axis_point[0], axis_point[1]])
            vertex_offset = 1

        # Add vertices from all surfaces
        # Note: surfaces include closure point, so we remove it
        n_points_per_surface = []
        for surface in surfaces:
            # Remove closure point (last point = first point)
            surface_points = surface[:-1]
            n_points = len(surface_points)
            n_points_per_surface.append(n_points)
            vertices_list.extend(surface_points.tolist())

        vertices = np.array(vertices_list)

        # Build elements
        current_vertex = vertex_offset

        # If axis point exists, create triangles from axis to first surface
        if axis_point is not None:
            n_first = n_points_per_surface[0]
            axis_idx = 0

            for i in range(n_first):
                # Triangle: axis, point i, point (i+1) % n
                v0 = axis_idx
                v1 = current_vertex + i
                v2 = current_vertex + ((i + 1) % n_first)
                elements_list.append([v0, v1, v2])

            current_vertex += n_first

        # Between each pair of surfaces
        for surf_idx in range(len(surfaces) - 1):
            n_inner = n_points_per_surface[surf_idx]
            n_outer = n_points_per_surface[surf_idx + 1]

            # For now, require same number of points on each surface
            if n_inner != n_outer:
                raise ValueError(
                    f"Surfaces must have same number of points: "
                    f"surface {surf_idx} has {n_inner}, surface {surf_idx+1} has {n_outer}"
                )

            n = n_inner
            inner_start = current_vertex if axis_point is None and surf_idx == 0 else current_vertex - n
            outer_start = current_vertex

            for i in range(n):
                # Indices for quad: inner[i], inner[i+1], outer[i], outer[i+1]
                i_inner_0 = inner_start + i
                i_inner_1 = inner_start + ((i + 1) % n)
                i_outer_0 = outer_start + i
                i_outer_1 = outer_start + ((i + 1) % n)

                # Split quad into 2 triangles
                # Triangle 1: inner[i], outer[i], inner[i+1]
                elements_list.append([i_inner_0, i_outer_0, i_inner_1])

                # Triangle 2: inner[i+1], outer[i], outer[i+1]
                elements_list.append([i_inner_1, i_outer_0, i_outer_1])

            current_vertex += n_outer

        elements = np.array(elements_list, dtype=np.int32)

        return vertices, elements

    def check_quality(
        self,
        vertices: np.ndarray,
        elements: np.ndarray
    ) -> dict:
        """
        Check mesh quality metrics.

        Convenience method that calls compute_mesh_quality.

        Args:
            vertices: np.ndarray shape (N, 2) - vertex coordinates
            elements: np.ndarray shape (E, 3) - element connectivity

        Returns:
            Dictionary with quality metrics
        """
        return compute_mesh_quality(vertices, elements)

    def create_boundary(
        self,
        surface: np.ndarray,
        densify: bool = False,
        target_spacing: Optional[float] = None
    ) -> np.ndarray:
        """
        Create boundary polyline from a flux surface.

        Takes a closed surface polyline and optionally densifies it to
        achieve uniform spacing. This is useful for creating inner/outer
        boundaries for unstructured mesh generation.

        Args:
            surface: np.ndarray shape (M, 2) - closed surface polyline (R, Z)
            densify: If True, add points to achieve uniform spacing
            target_spacing: Target spacing for densification (required if densify=True)

        Returns:
            np.ndarray shape (N, 2) - boundary polyline (R, Z), closed
        """
        if len(surface) == 0:
            raise ValueError("Surface must have at least one point")

        # Ensure surface is closed (first point = last point)
        if not np.allclose(surface[0], surface[-1], atol=1e-10):
            # Close the surface if not already closed
            surface = np.vstack([surface, surface[0:1]])

        if not densify:
            # Return surface as-is (already closed)
            return surface.copy()

        # Densify the boundary to achieve uniform spacing
        if target_spacing is None or target_spacing <= 0:
            raise ValueError("target_spacing must be positive when densify=True")

        # Compute cumulative arc length
        points = surface[:-1]  # Remove closure point temporarily
        n_points = len(points)

        # Compute distances between consecutive points
        diffs = np.diff(points, axis=0, prepend=points[-1:])
        distances = np.linalg.norm(diffs, axis=1)

        # Cumulative distance
        cum_dist = np.zeros(n_points + 1)
        cum_dist[1:] = np.cumsum(distances)
        total_length = cum_dist[-1]

        # Determine number of new points needed
        n_new_points = int(np.ceil(total_length / target_spacing))
        if n_new_points < n_points:
            n_new_points = n_points

        # Create uniformly spaced arc length samples
        new_arc_lengths = np.linspace(0, total_length, n_new_points, endpoint=False)

        # Interpolate R and Z at new arc lengths
        new_R = np.interp(new_arc_lengths, cum_dist[:-1], points[:, 0], period=total_length)
        new_Z = np.interp(new_arc_lengths, cum_dist[:-1], points[:, 1], period=total_length)

        # Create new boundary
        new_boundary = np.column_stack([new_R, new_Z])

        # Close the boundary
        new_boundary = np.vstack([new_boundary, new_boundary[0:1]])

        return new_boundary

    def build_unstructured_SOL(
        self,
        inner_poly: np.ndarray,
        outer_poly: np.ndarray,
        target_size: float
    ) -> Tuple[np.ndarray, np.ndarray]:
        """
        Build unstructured triangular mesh for SOL (scrape-off layer) region.

        Uses Gmsh to generate an unstructured mesh between inner and outer
        boundaries. The inner boundary vertices are preserved to allow sharing
        with the structured mesh.

        Args:
            inner_poly: np.ndarray shape (M, 2) - inner boundary polyline (R, Z)
            outer_poly: np.ndarray shape (N, 2) - outer boundary polyline (R, Z)
            target_size: Target element size for mesh generation

        Returns:
            Tuple (vertices, elements):
            - vertices: np.ndarray shape (V, 2) - (R, Z) coordinates
            - elements: np.ndarray shape (E, 3) - triangle vertex indices

        Raises:
            RuntimeError: If Gmsh is not available
            ValueError: If boundaries are invalid (e.g., inner larger than outer)
        """
        if gmsh is None:
            raise RuntimeError("Gmsh is not installed. Install with: pip install gmsh")

        if len(inner_poly) == 0 or len(outer_poly) == 0:
            raise ValueError("Inner and outer boundaries must have at least one point")

        # Validate that inner boundary is inside outer boundary
        # Simple check: compare average radii
        inner_avg_R = np.mean(inner_poly[:-1, 0])
        outer_avg_R = np.mean(outer_poly[:-1, 0])
        inner_max_dist = np.max(np.linalg.norm(inner_poly[:-1] - [inner_avg_R, 0], axis=1))
        outer_min_dist = np.min(np.linalg.norm(outer_poly[:-1] - [outer_avg_R, 0], axis=1))

        if inner_max_dist >= outer_min_dist:
            raise ValueError("Inner boundary appears to be outside outer boundary")

        try:
            # Initialize Gmsh
            gmsh.initialize()
            gmsh.model.add("SOL_mesh")

            # Create inner boundary curve loop
            inner_points = inner_poly[:-1]  # Remove closure point
            inner_point_tags = []
            for i, point in enumerate(inner_points):
                tag = gmsh.model.geo.addPoint(point[0], point[1], 0.0, target_size)
                inner_point_tags.append(tag)

            # Create inner boundary lines
            inner_line_tags = []
            for i in range(len(inner_point_tags)):
                i_next = (i + 1) % len(inner_point_tags)
                line_tag = gmsh.model.geo.addLine(inner_point_tags[i], inner_point_tags[i_next])
                inner_line_tags.append(line_tag)

            # Create inner curve loop
            inner_loop = gmsh.model.geo.addCurveLoop(inner_line_tags)

            # Create outer boundary curve loop
            outer_points = outer_poly[:-1]  # Remove closure point
            outer_point_tags = []
            for i, point in enumerate(outer_points):
                tag = gmsh.model.geo.addPoint(point[0], point[1], 0.0, target_size)
                outer_point_tags.append(tag)

            # Create outer boundary lines
            outer_line_tags = []
            for i in range(len(outer_point_tags)):
                i_next = (i + 1) % len(outer_point_tags)
                line_tag = gmsh.model.geo.addLine(outer_point_tags[i], outer_point_tags[i_next])
                outer_line_tags.append(line_tag)

            # Create outer curve loop
            outer_loop = gmsh.model.geo.addCurveLoop(outer_line_tags)

            # Create surface (outer - inner)
            surface = gmsh.model.geo.addPlaneSurface([outer_loop, inner_loop])

            # Synchronize CAD model
            gmsh.model.geo.synchronize()

            # Set mesh size
            gmsh.option.setNumber("Mesh.CharacteristicLengthMin", target_size * 0.5)
            gmsh.option.setNumber("Mesh.CharacteristicLengthMax", target_size * 2.0)

            # Generate 2D mesh
            gmsh.model.mesh.generate(2)

            # Extract nodes (vertices)
            node_tags, node_coords, _ = gmsh.model.mesh.getNodes()
            n_nodes = len(node_tags)

            # Reshape coordinates to (n_nodes, 3) and extract R, Z
            coords_3d = node_coords.reshape((n_nodes, 3))
            vertices = coords_3d[:, :2]  # Take only R, Z (discard Z=0)

            # Extract triangular elements
            elem_types, elem_tags_list, elem_node_tags_list = gmsh.model.mesh.getElements(2)

            # Find triangle element type (type 2 in Gmsh)
            triangle_idx = None
            for i, elem_type in enumerate(elem_types):
                if elem_type == 2:  # Triangle
                    triangle_idx = i
                    break

            if triangle_idx is None:
                raise RuntimeError("No triangular elements found in Gmsh mesh")

            # Get triangle connectivity
            triangle_node_tags = elem_node_tags_list[triangle_idx]
            n_triangles = len(triangle_node_tags) // 3

            # Reshape to (n_triangles, 3) and convert to 0-based indexing
            elements_1based = triangle_node_tags.reshape((n_triangles, 3)).astype(np.int32)

            # Create mapping from Gmsh node tags to 0-based indices
            node_tag_to_idx = {tag: idx for idx, tag in enumerate(node_tags)}
            elements = np.array([
                [node_tag_to_idx[elements_1based[i, j]] for j in range(3)]
                for i in range(n_triangles)
            ], dtype=np.int32)

            return vertices, elements

        except Exception as e:
            logger.error(f"Gmsh meshing failed: {e}")
            raise RuntimeError(f"Gmsh meshing failed: {e}")
        finally:
            # Cleanup Gmsh
            gmsh.finalize()

    def build(
        self,
        surfaces: List[np.ndarray],
        axis_point: Optional[Tuple[float, float]] = None,
        outer_boundary: Optional[np.ndarray] = None,
        target_size: float = 0.1,
        merge_tolerance: float = 1e-6
    ) -> Tuple[np.ndarray, np.ndarray]:
        """
        Build complete mesh by merging structured and SOL regions.

        Creates a structured mesh from flux surfaces, optionally adds an
        unstructured SOL mesh, and merges them with duplicate node removal.

        Args:
            surfaces: List of flux surface polylines (each shape (M, 2) with R, Z)
            axis_point: Optional (R, Z) tuple for magnetic axis point
            outer_boundary: Optional outer boundary for SOL mesh (shape (N, 2))
            target_size: Target element size for SOL mesh (if outer_boundary provided)
            merge_tolerance: Tolerance for merging duplicate vertices at boundary

        Returns:
            Tuple (vertices, elements):
            - vertices: np.ndarray shape (V, 2) - (R, Z) coordinates
            - elements: np.ndarray shape (E, 3) - triangle vertex indices
        """
        if len(surfaces) == 0:
            raise ValueError("At least one surface required")

        # Build structured mesh
        struct_vertices, struct_elements = self.build_structured(surfaces, axis_point)

        # If no outer boundary, return structured mesh only
        if outer_boundary is None:
            return struct_vertices, struct_elements

        # Build SOL mesh
        # Inner boundary is the last surface
        inner_boundary = surfaces[-1]

        sol_vertices, sol_elements = self.build_unstructured_SOL(
            inner_boundary,
            outer_boundary,
            target_size
        )

        # Merge meshes
        # Strategy:
        # 1. Identify boundary vertices from structured mesh (last surface)
        # 2. Find matching vertices in SOL mesh
        # 3. Create unified vertex list
        # 4. Remap element indices

        # Get structured mesh boundary vertices (last surface, excluding closure)
        n_points_per_surface = len(surfaces[-1]) - 1
        n_struct_vertices = len(struct_vertices)

        # Find offset to last surface in structured mesh
        if axis_point is not None:
            # axis + all surface points
            offset_to_last_surface = 1 + sum(len(s) - 1 for s in surfaces[:-1])
        else:
            # just surface points
            offset_to_last_surface = sum(len(s) - 1 for s in surfaces[:-1])

        struct_boundary_indices = list(range(
            offset_to_last_surface,
            offset_to_last_surface + n_points_per_surface
        ))

        struct_boundary_vertices = struct_vertices[struct_boundary_indices]

        # Find matching vertices in SOL mesh
        # SOL mesh should have these boundary vertices
        sol_to_struct_map = {}  # SOL vertex index -> struct vertex index

        for sol_idx in range(len(sol_vertices)):
            sol_vertex = sol_vertices[sol_idx]

            # Find closest struct boundary vertex
            distances = np.linalg.norm(struct_boundary_vertices - sol_vertex, axis=1)
            min_dist_idx = np.argmin(distances)
            min_dist = distances[min_dist_idx]

            if min_dist < merge_tolerance:
                # This SOL vertex matches a struct boundary vertex
                struct_idx = struct_boundary_indices[min_dist_idx]
                sol_to_struct_map[sol_idx] = struct_idx

        # Create merged vertex list
        # Start with all structured vertices
        merged_vertices = struct_vertices.copy()

        # Add SOL vertices that are NOT on the boundary
        sol_vertex_to_merged = {}  # SOL index -> merged index
        for sol_idx in range(len(sol_vertices)):
            if sol_idx in sol_to_struct_map:
                # This SOL vertex is on boundary, map to struct vertex
                sol_vertex_to_merged[sol_idx] = sol_to_struct_map[sol_idx]
            else:
                # This is a new vertex, add it
                new_idx = len(merged_vertices)
                merged_vertices = np.vstack([merged_vertices, sol_vertices[sol_idx:sol_idx+1]])
                sol_vertex_to_merged[sol_idx] = new_idx

        # Create merged element list
        # Start with structured elements (no remapping needed)
        merged_elements = struct_elements.copy()

        # Add SOL elements with remapped indices
        for sol_elem in sol_elements:
            remapped_elem = [
                sol_vertex_to_merged[sol_elem[0]],
                sol_vertex_to_merged[sol_elem[1]],
                sol_vertex_to_merged[sol_elem[2]]
            ]
            merged_elements = np.vstack([merged_elements, [remapped_elem]])

        return merged_vertices, merged_elements


def compute_mesh_quality(
    vertices: np.ndarray,
    elements: np.ndarray
) -> dict:
    """
    Compute mesh quality metrics.

    Delegates to MeshQualityAnalyzer for centralized quality computation.

    Calculates various quality measures for triangular elements:
    - Aspect ratios (ratio of longest to shortest edge)
    - Minimum angles in each element
    - Number of inverted elements (negative area)

    Args:
        vertices: np.ndarray shape (N, 2) - (R, Z) coordinates
        elements: np.ndarray shape (E, 3) - triangle vertex indices

    Returns:
        Dictionary containing:
        - 'aspect_ratios': array of aspect ratios for each element
        - 'min_angles': array of minimum angles (degrees) for each element
        - 'areas': array of triangle areas
        - 'n_inverted': number of inverted (negative area) elements
        - 'min_angle_min': minimum of all minimum angles
        - 'min_angle_mean': mean of minimum angles
        - 'aspect_ratio_max': maximum aspect ratio
        - 'aspect_ratio_mean': mean aspect ratio
    """
    # Get core metrics from MeshQualityAnalyzer
    metrics = MeshQualityAnalyzer.compute_all_metrics(vertices, elements)

    # Check for inverted elements
    inverted = MeshQualityAnalyzer.check_inverted_elements(vertices, elements)

    # Build result dictionary with backward compatibility
    quality_dict = {
        'aspect_ratios': metrics['aspect_ratios'].tolist(),  # Convert to list for compatibility
        'min_angles': metrics['min_angles'].tolist(),
        'areas': metrics['areas'],  # Keep as array
        'n_inverted': len(inverted),
    }

    # Add summary statistics
    min_angles = metrics['min_angles']
    aspect_ratios = metrics['aspect_ratios']

    if len(min_angles) > 0:
        quality_dict['min_angle_min'] = float(np.min(min_angles))
        quality_dict['min_angle_mean'] = float(np.mean(min_angles))

    if len(aspect_ratios) > 0:
        # Filter out inf values for statistics
        finite_ratios = aspect_ratios[np.isfinite(aspect_ratios)]
        if len(finite_ratios) > 0:
            quality_dict['aspect_ratio_max'] = float(np.max(finite_ratios))
            quality_dict['aspect_ratio_mean'] = float(np.mean(finite_ratios))
        else:
            quality_dict['aspect_ratio_max'] = float('inf')
            quality_dict['aspect_ratio_mean'] = float('inf')

    return quality_dict
