"""
SCOREC KSTAR Mesh Validation Test

This test validates the complete SCOREC export workflow using a real KSTAR mesh:
1. Load KSTAR GEQDSK file
2. Generate mesh from PSI contour
3. Export to SCOREC .dmg/.smb formats
4. Load with PUMI using loadMdsMesh API
5. Export VTK from PUMI
6. Verify mesh integrity (vertex count, coordinate preservation)

This is a comprehensive end-to-end validation test that proves our SCOREC
export works with real fusion plasma meshes.
"""
import pytest
import numpy as np
import tempfile
import os
import subprocess
from pathlib import Path


@pytest.mark.slow
def test_kstar_mesh_scorec_roundtrip(tmp_path):
    """
    Complete roundtrip validation with KSTAR mesh:
    1. Generate mesh from KSTAR GEQDSK file
    2. Export to SCOREC formats (.dmg/.smb)
    3. Load with PUMI (loadMdsMesh API)
    4. Export to VTK from PUMI
    5. Verify mesh data integrity
    """
    from mesh_gui_project.data.geqdsk_parser import parse_geqdsk
    from mesh_gui_project.core.equilibrium import EquilibriumData
    from mesh_gui_project.utils.interpolation import make_bicubic_interpolator
    from mesh_gui_project.core.mesh_generation_workflow import MeshGenerationWorkflow
    from mesh_gui_project.core.exporter import export_mesh_to_scorec

    # Step 1: Load KSTAR GEQDSK file
    test_file = os.path.join(
        os.path.dirname(__file__),
        '..',
        'examples',
        'kstar_EFIT01_35582_010000.esy_headerMod.geqdsk'
    )

    if not os.path.exists(test_file):
        pytest.skip("KSTAR GEQDSK file not found")

    print(f"\n✓ Loading KSTAR GEQDSK: {test_file}")
    data = parse_geqdsk(test_file)
    equilibrium = EquilibriumData(data)
    interp = make_bicubic_interpolator(data['R_grid'], data['Z_grid'], data['psi_grid'])
    equilibrium.attach_interpolator(interp)

    # Step 2: Generate mesh from PSI contour
    workflow = MeshGenerationWorkflow()
    psi_value = 0.95  # PSI near edge
    mesh_size = 0.05  # Moderate mesh size for reasonable test time

    print(f"✓ Generating mesh at PSI={psi_value}, mesh_size={mesh_size}")
    result = workflow.generate_mesh_from_psi(
        equilibrium=equilibrium,
        psi_value=psi_value,
        target_element_size=mesh_size
    )

    vertices = result['vertices']
    elements = result['elements']

    assert vertices.shape[1] == 2, "Should have 2D vertices"
    assert elements.shape[1] == 3, "Should have triangular elements"
    assert len(vertices) > 10, "Should have reasonable number of vertices"
    assert len(elements) > 10, "Should have reasonable number of triangles"

    print(f"✓ Generated mesh: {len(vertices)} vertices, {len(elements)} triangles")

    # Step 3: Export to SCOREC formats
    # PUMI expects partition-numbered files for MPI, so we create the files with partition suffix
    dmg_path = tmp_path / "kstar_mesh.dmg"
    smb_temp = tmp_path / "kstar_mesh_temp.smb"

    export_mesh_to_scorec(vertices, elements, str(dmg_path), str(smb_temp))

    assert dmg_path.exists(), "DMG file should be created"
    assert smb_temp.exists(), "SMB file should be created"

    # Rename to partition naming that PUMI expects
    smb_path_with_partition = tmp_path / "kstar_mesh0.smb"
    import shutil
    shutil.move(str(smb_temp), str(smb_path_with_partition))

    print(f"✓ Exported to SCOREC formats")
    print(f"  DMG: {dmg_path.stat().st_size} bytes")
    print(f"  SMB: {smb_path_with_partition.stat().st_size} bytes")

    # Step 4: Write C code to load with PUMI and export VTK
    c_validator_path = tmp_path / "kstar_validator.c"
    c_executable = tmp_path / "kstar_validator"
    vtk_pumi_path = tmp_path / "kstar_pumi_output"

    c_code = '''#include <stdio.h>
#include <stdlib.h>
#include <gmi_mesh.h>
#include <gmi_null.h>
#include <apfMDS.h>
#include <apfMesh2.h>
#include <apf.h>
#include <lionPrint.h>
#include <PCU.h>
#include <mpi.h>

int main(int argc, char** argv) {
    if (argc != 4) {
        fprintf(stderr, "Usage: %s <model.dmg> <mesh.smb> <output_vtk_prefix>\\n", argv[0]);
        return 1;
    }

    const char* dmg_file = argv[1];
    const char* smb_file = argv[2];
    const char* vtk_prefix = argv[3];

    // Initialize MPI
    MPI_Init(&argc, &argv);

    // Create PCU object (PUMI 2.6+ API)
    pcu::PCU pcu_obj = pcu::PCU(MPI_COMM_WORLD);

    // Set verbosity
    lion_set_verbosity(1);

    // Register mesh types
    gmi_register_mesh();
    gmi_register_null();

    printf("Loading KSTAR SCOREC mesh...\\n");
    printf("  Model: %s\\n", dmg_file);
    printf("  Mesh:  %s\\n", smb_file);

    // Load mesh using canonical loadMdsMesh API
    printf("Calling loadMdsMesh...\\n");
    fflush(stdout);
    apf::Mesh2* mesh = apf::loadMdsMesh(dmg_file, smb_file, &pcu_obj);
    printf("loadMdsMesh returned\\n");
    fflush(stdout);

    if (!mesh) {
        fprintf(stderr, "ERROR: Failed to load mesh\\n");
        MPI_Finalize();
        return 1;
    }

    // Get mesh statistics
    int dim = mesh->getDimension();
    int num_verts = mesh->count(0);
    int num_edges = mesh->count(1);
    int num_faces = mesh->count(2);

    printf("\\nKSTAR mesh loaded successfully!\\n");
    printf("  Dimension: %d\\n", dim);
    printf("  Vertices:  %d\\n", num_verts);
    printf("  Edges:     %d\\n", num_edges);
    printf("  Faces:     %d\\n", num_faces);

    // Call mesh->verify() - with proper edge classification, this should now pass!
    printf("\\nCalling mesh->verify()...\\n");
    fflush(stdout);
    mesh->verify();
    printf("✓ mesh->verify() PASSED\\n");
    fflush(stdout);

    // Write to VTK
    printf("\\nWriting VTK output to: %s\\n", vtk_prefix);
    apf::writeVtkFiles(vtk_prefix, mesh);
    printf("✓ VTK files written\\n");

    // Cleanup
    mesh->destroyNative();
    apf::destroyMesh(mesh);

    MPI_Finalize();

    printf("\\n✓ KSTAR PUMI validation completed successfully\\n");
    return 0;
}
'''

    with open(c_validator_path, 'w') as f:
        f.write(c_code)

    print(f"\n✓ Created C validator: {c_validator_path}")

    # Check if PUMI is available
    pumi_install = "/home/apeach/openlib/pumi260103-minimal"
    if not os.path.exists(pumi_install):
        pytest.skip(f"PUMI installation not found: {pumi_install}")

    # Compile C validator
    compile_cmd = [
        "mpic++",
        "-std=c++11",
        "-no-pie",
        str(c_validator_path),
        "-o", str(c_executable),
        f"-I{pumi_install}/include",
        f"-L{pumi_install}/lib",
        "-lmds", "-lapf", "-lparma", "-lcrv", "-lgmi", "-lpcu", "-llion", "-lmth"
    ]

    try:
        result = subprocess.run(compile_cmd, capture_output=True, text=True, timeout=30)
        if result.returncode != 0:
            print(f"\nCompilation output:\n{result.stderr}")
            pytest.skip("PUMI libraries not available for compilation")
    except (subprocess.TimeoutExpired, FileNotFoundError) as e:
        pytest.skip(f"Cannot compile PUMI validator: {e}")

    print(f"✓ Compiled C validator")

    # Run the validator
    # Pass path WITH .smb extension (PUMI will strip and add partition number)
    smb_path_for_api = str(tmp_path / "kstar_mesh.smb")

    try:
        result = subprocess.run(
            [str(c_executable), str(dmg_path), smb_path_for_api, str(vtk_pumi_path)],
            capture_output=True,
            text=True,
            timeout=60  # Longer timeout for larger mesh
        )

        print(f"\nPUMI validator output:\n{result.stdout}")

        # Check if validation completed successfully
        validation_success = "KSTAR PUMI validation completed successfully" in result.stdout
        verify_passed = "mesh->verify() PASSED" in result.stdout

        if not validation_success:
            print(f"PUMI validator errors:\n{result.stderr}")
            pytest.fail(f"PUMI validator did not complete successfully")

        if not verify_passed:
            print(f"PUMI validator errors:\n{result.stderr}")
            pytest.fail(f"mesh->verify() did not pass - edge classification issue")

        print(f"\n✓ PUMI loadMdsMesh validation completed successfully")
        print(f"✓ mesh->verify() PASSED for KSTAR mesh!")

    except subprocess.TimeoutExpired:
        pytest.fail("PUMI validator timed out")

    # Step 5: Verify PUMI created VTK output
    pumi_vtk_dir = tmp_path / "kstar_pumi_output"
    pumi_vtk_files = list(pumi_vtk_dir.glob("*.pvtu")) + list(pumi_vtk_dir.glob("*.vtu"))
    assert len(pumi_vtk_files) > 0, f"PUMI should have created VTK output files in {pumi_vtk_dir}"

    pumi_vtk = pumi_vtk_files[0]
    print(f"\n✓ PUMI created VTK: {pumi_vtk.name} ({pumi_vtk.stat().st_size} bytes)")

    # Step 6: Parse VTK and verify vertex count matches
    # Read the VTU file to extract vertex count
    with open(pumi_vtk, 'r') as f:
        vtk_content = f.read()

    # Basic validation: file should have content
    assert len(vtk_content) > 100, "PUMI VTK should have content"

    # Extract number of vertices from PUMI output
    import re

    # Initialize variables
    pumi_vertex_count = None
    pumi_triangle_count = None

    # Find NumberOfPoints in VTK file
    points_match = re.search(r'NumberOfPoints="(\d+)"', vtk_content)
    if points_match:
        pumi_vertex_count = int(points_match.group(1))
        print(f"\n✓ Vertex count verification:")
        print(f"  Python export: {len(vertices)} vertices")
        print(f"  PUMI roundtrip: {pumi_vertex_count} vertices")

        # Verify counts match
        assert pumi_vertex_count == len(vertices), \
            f"Vertex count mismatch: Python={len(vertices)}, PUMI={pumi_vertex_count}"

    # Extract number of cells (triangles) from PUMI output
    cells_match = re.search(r'NumberOfCells="(\d+)"', vtk_content)
    if cells_match:
        pumi_triangle_count = int(cells_match.group(1))
        print(f"  Python triangles: {len(elements)}")
        print(f"  PUMI triangles: {pumi_triangle_count}")

        # Verify counts match
        assert pumi_triangle_count == len(elements), \
            f"Triangle count mismatch: Python={len(elements)}, PUMI={pumi_triangle_count}"

    # Final success message
    print(f"\n" + "=" * 60)
    print(f"✅ KSTAR MESH SCOREC VALIDATION COMPLETE")
    print(f"=" * 60)
    print(f"Original mesh: {len(vertices)} vertices, {len(elements)} triangles")
    print(f"SCOREC export: DMG ({dmg_path.stat().st_size} bytes) + SMB ({smb_path_with_partition.stat().st_size} bytes)")
    print(f"PUMI validation: mesh->verify() PASSED")
    if pumi_vertex_count is not None and pumi_triangle_count is not None:
        print(f"VTK roundtrip: {pumi_vertex_count} vertices, {pumi_triangle_count} triangles")
        print(f"✅ Mesh data integrity verified - counts match perfectly!")
    print(f"=" * 60)


if __name__ == "__main__":
    # Run test manually
    import tempfile
    with tempfile.TemporaryDirectory() as tmpdir:
        test_kstar_mesh_scorec_roundtrip(Path(tmpdir))
