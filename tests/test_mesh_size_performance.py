"""
Test that mesh generation completes in reasonable time for various mesh sizes.

Regression test for bug where mesh size 0.02 would stall indefinitely.
"""
import pytest
import numpy as np
import time
from mesh_gui_project.core.new_mesher import ContourMesher
from mesh_gui_project.data.geqdsk_parser import parse_geqdsk


@pytest.fixture
def simple_boundary():
    """Simple square boundary for quick tests."""
    return np.array([
        [1.5, -0.5],
        [2.5, -0.5],
        [2.5, 0.5],
        [1.5, 0.5],
        [1.5, -0.5]
    ])


@pytest.fixture
def realistic_boundary():
    """Realistic boundary from GEQDSK file."""
    geqdsk_path = "examples/kstar_EFIT01_35582_010000.esy_headerMod.geqdsk"
    eq_data = parse_geqdsk(geqdsk_path)
    return eq_data['limiter']


def test_mesh_size_0_05_completes_quickly(simple_boundary):
    """Test that mesh size 0.05 completes in < 2 seconds."""
    mesher = ContourMesher()

    start = time.time()
    vertices, elements = mesher.generate_mesh(simple_boundary, target_element_size=0.05)
    elapsed = time.time() - start

    assert elapsed < 2.0, f"Mesh generation too slow: {elapsed:.2f}s"
    assert len(vertices) > 0
    assert len(elements) > 0


def test_mesh_size_0_03_completes_quickly(simple_boundary):
    """Test that mesh size 0.03 completes in < 2 seconds."""
    mesher = ContourMesher()

    start = time.time()
    vertices, elements = mesher.generate_mesh(simple_boundary, target_element_size=0.03)
    elapsed = time.time() - start

    assert elapsed < 2.0, f"Mesh generation too slow: {elapsed:.2f}s"
    assert len(vertices) > 0
    assert len(elements) > 0


def test_mesh_size_0_02_completes_quickly(simple_boundary):
    """
    Test that mesh size 0.02 completes in < 2 seconds.

    Regression test for bug where 0.02 would stall indefinitely due to
    per-point mesh size constraints causing excessive refinement.
    """
    mesher = ContourMesher()

    start = time.time()
    vertices, elements = mesher.generate_mesh(simple_boundary, target_element_size=0.02)
    elapsed = time.time() - start

    assert elapsed < 2.0, f"Mesh generation too slow: {elapsed:.2f}s"
    assert len(vertices) > 0
    assert len(elements) > 0


def test_realistic_boundary_mesh_size_0_03(realistic_boundary):
    """Test realistic boundary with mesh size 0.03."""
    mesher = ContourMesher()

    start = time.time()
    vertices, elements = mesher.generate_mesh(realistic_boundary, target_element_size=0.03)
    elapsed = time.time() - start

    assert elapsed < 5.0, f"Mesh generation too slow: {elapsed:.2f}s"
    assert len(vertices) > 0
    assert len(elements) > 0
    print(f"Generated {len(vertices)} vertices, {len(elements)} triangles in {elapsed:.2f}s")


def test_realistic_boundary_mesh_size_0_02(realistic_boundary):
    """
    Test realistic boundary with mesh size 0.02.

    This is the critical regression test - this used to stall indefinitely.
    """
    mesher = ContourMesher()

    start = time.time()
    vertices, elements = mesher.generate_mesh(realistic_boundary, target_element_size=0.02)
    elapsed = time.time() - start

    assert elapsed < 5.0, f"Mesh generation too slow: {elapsed:.2f}s"
    assert len(vertices) > 0
    assert len(elements) > 0
    print(f"Generated {len(vertices)} vertices, {len(elements)} triangles in {elapsed:.2f}s")


def test_finer_mesh_produces_more_elements(simple_boundary):
    """Test that finer mesh sizes produce more elements."""
    mesher = ContourMesher()

    _, elements_05 = mesher.generate_mesh(simple_boundary, target_element_size=0.05)
    _, elements_03 = mesher.generate_mesh(simple_boundary, target_element_size=0.03)
    _, elements_02 = mesher.generate_mesh(simple_boundary, target_element_size=0.02)

    assert len(elements_02) > len(elements_03) > len(elements_05), \
        "Finer mesh should produce more elements"
