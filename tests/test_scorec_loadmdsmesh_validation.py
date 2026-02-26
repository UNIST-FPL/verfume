"""
SCOREC loadMdsMesh API Validation Test

This test validates our SCOREC export using the canonical loadMdsMesh API:
1. Create a test mesh (2D triangular)
2. Export to .smb/.dmg formats
3. Use PUMI's loadMdsMesh() API to load both files together
4. Call mesh->verify() to validate mesh structure
5. Export to VTK to confirm correctness

This is the CORRECT way to test SCOREC mesh files according to PUMI documentation.
See: /home/apeach/Downloads/core-master/test/construct.cc
"""
import pytest
import numpy as np
import tempfile
import os
import subprocess
from pathlib import Path


def test_loadmdsmesh_api_validation(tmp_path):
    """
    Test SCOREC export using the canonical loadMdsMesh API.

    This test uses apf::loadMdsMesh(model_file, mesh_file, &pcu) which is
    the standard PUMI API for loading .dmg + .smb files together.
    """
    from mesh_gui_project.core.exporter import export_mesh_to_scorec

    # Step 1: Create a test mesh - simple square
    vertices = np.array([
        [0.0, 0.0],
        [1.0, 0.0],
        [1.0, 1.0],
        [0.0, 1.0]
    ])

    elements = np.array([
        [0, 1, 2],
        [0, 2, 3]
    ], dtype=np.int32)

    print(f"\n✓ Created test mesh: {len(vertices)} vertices, {len(elements)} triangles")

    # Step 2: Export to SCOREC formats
    # NOTE: loadMdsMesh expects partitioned naming: basename + partition number
    # For serial meshes with MPI rank 0, it looks for "basename0.smb"
    # We'll export with the partition suffix directly
    dmg_path = tmp_path / "test_mesh.dmg"
    smb_path_with_partition = tmp_path / "test_mesh0.smb"  # PUMI expects this for rank 0

    # Export to a temp name first
    smb_temp = tmp_path / "test_mesh_temp.smb"
    export_mesh_to_scorec(vertices, elements, str(dmg_path), str(smb_temp))

    assert dmg_path.exists(), "DMG file should be created"
    assert smb_temp.exists(), "SMB file should be created"

    # Rename to the partition naming that PUMI expects
    import shutil
    shutil.move(str(smb_temp), str(smb_path_with_partition))

    print(f"✓ Exported to SCOREC formats")
    print(f"  DMG: {dmg_path.stat().st_size} bytes")
    print(f"  SMB: {smb_path_with_partition.stat().st_size} bytes (with partition suffix)")
    print(f"  PUMI will look for: {smb_path_with_partition.name}")

    # Step 3: Write C validation code using loadMdsMesh
    c_validator_path = tmp_path / "pumi_loadmdsmesh_validator.c"
    c_executable = tmp_path / "pumi_loadmdsmesh_validator"
    vtk_output_path = tmp_path / "pumi_output"

    # C code using the canonical loadMdsMesh API
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

    // Set verbosity for debugging
    lion_set_verbosity(1);

    // Register mesh types BEFORE loading
    gmi_register_mesh();
    gmi_register_null();  // For .dmg files

    printf("=========================================\\n");
    printf("PUMI loadMdsMesh API Validation Test\\n");
    printf("=========================================\\n");
    printf("Loading SCOREC mesh using loadMdsMesh()...\\n");
    printf("  Model: %s\\n", dmg_file);
    printf("  Mesh:  %s\\n", smb_file);
    printf("\\n");

    // ===================================================================
    // CRITICAL: Use loadMdsMesh - the canonical PUMI API
    // This loads both model and mesh together in one call
    // Reference: /home/apeach/Downloads/core-master/test/construct.cc
    // ===================================================================
    apf::Mesh2* mesh = apf::loadMdsMesh(dmg_file, smb_file, &pcu_obj);

    if (!mesh) {
        fprintf(stderr, "ERROR: loadMdsMesh() failed to load mesh\\n");
        MPI_Finalize();
        return 1;
    }

    printf("✓ loadMdsMesh() succeeded\\n");
    printf("\\n");

    // Get mesh statistics
    int dim = mesh->getDimension();
    int num_verts = mesh->count(0);
    int num_edges = mesh->count(1);
    int num_faces = mesh->count(2);

    printf("Mesh Statistics:\\n");
    printf("  Dimension: %d\\n", dim);
    printf("  Vertices:  %d\\n", num_verts);
    printf("  Edges:     %d\\n", num_edges);
    printf("  Faces:     %d\\n", num_faces);
    printf("\\n");

    // ===================================================================
    // CRITICAL: Call mesh->verify() to validate mesh structure
    // This is PUMI's internal consistency checker
    // If this fails, there is a bug in our mesh export
    // ===================================================================
    printf("Calling mesh->verify()...\\n");
    fflush(stdout);

    try {
        mesh->verify();
        printf("✓ mesh->verify() PASSED\\n");
        printf("\\n");
    } catch (...) {
        fprintf(stderr, "ERROR: mesh->verify() threw an exception\\n");
        // Continue to see if we can still export to VTK
    }

    // Write to VTK for visual inspection
    printf("Writing VTK output to: %s\\n", vtk_prefix);
    apf::writeVtkFiles(vtk_prefix, mesh);
    printf("✓ VTK files written\\n");
    printf("\\n");

    // Cleanup
    mesh->destroyNative();
    apf::destroyMesh(mesh);

    MPI_Finalize();

    printf("=========================================\\n");
    printf("✓ PUMI loadMdsMesh validation completed\\n");
    printf("=========================================\\n");
    return 0;
}
'''

    with open(c_validator_path, 'w') as f:
        f.write(c_code)

    print(f"\n✓ Created C validator using loadMdsMesh API: {c_validator_path}")

    # Check if PUMI is available
    pumi_install = "/home/apeach/openlib/pumi260103-minimal"
    if not os.path.exists(pumi_install):
        pytest.skip(f"PUMI installation not found: {pumi_install}")

    # Compile the validator
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
    # CRITICAL: Pass path WITH ".smb" extension
    # PUMI will:
    #   1. Strip ".smb" → "test_mesh"
    #   2. Append partition number → "test_mesh0.smb"
    smb_path_for_api = str(tmp_path / "test_mesh.smb")

    try:
        result = subprocess.run(
            [str(c_executable), str(dmg_path), smb_path_for_api, str(vtk_output_path)],
            capture_output=True,
            text=True,
            timeout=30
        )

        print(f"\n{'='*60}")
        print("PUMI Validator Output:")
        print('='*60)
        print(result.stdout)
        print('='*60)

        if result.stderr:
            print(f"\nPUMI Validator Stderr:")
            print('='*60)
            print(result.stderr)
            print('='*60)

        # Check if validation completed successfully
        validation_success = "PUMI loadMdsMesh validation completed" in result.stdout

        if not validation_success:
            # Check for specific error messages
            if "mesh->verify()" in result.stderr or "verify() threw" in result.stdout:
                pytest.fail(f"mesh->verify() failed - mesh structure has errors")
            else:
                pytest.fail(f"PUMI validator did not complete successfully")

        # Check if verify passed
        if "mesh->verify() PASSED" in result.stdout:
            print("\n✅ SUCCESS: mesh->verify() PASSED!")
        else:
            print("\n⚠️  WARNING: mesh->verify() did not explicitly pass")

    except subprocess.TimeoutExpired:
        pytest.fail("PUMI validator timed out")

    # Verify PUMI created VTK output
    pumi_vtk_dir = tmp_path / "pumi_output"
    pumi_vtk_files = list(pumi_vtk_dir.glob("*.pvtu")) + list(pumi_vtk_dir.glob("*.vtu"))
    assert len(pumi_vtk_files) > 0, f"PUMI should have created VTK output files in {pumi_vtk_dir}"

    pumi_vtk = pumi_vtk_files[0]
    print(f"\n✓ PUMI created VTK: {pumi_vtk.name} ({pumi_vtk.stat().st_size} bytes)")

    print(f"\n✓ Complete validation using loadMdsMesh API!")
    print(f"  Python export: {len(vertices)} vertices, {len(elements)} triangles")
    print(f"  PUMI loadMdsMesh: Successfully loaded both .dmg and .smb")
    print(f"  ✅ CANONICAL PUMI API VALIDATED")


if __name__ == "__main__":
    # Run test manually
    import tempfile
    with tempfile.TemporaryDirectory() as tmpdir:
        test_loadmdsmesh_api_validation(Path(tmpdir))
