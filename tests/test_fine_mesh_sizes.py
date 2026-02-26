"""
Test that fine mesh sizes work correctly down to 0.001.

Regression test for bug where duplicate closing point in boundary
caused Gmsh to hang indefinitely.
"""
import pytest
import numpy as np
import time
from mesh_gui_project.core.new_mesher import ContourMesher
from mesh_gui_project.data.geqdsk_parser import parse_geqdsk


@pytest.fixture
def limiter_boundary():
    """Realistic limiter boundary from GEQDSK file."""
    geqdsk_path = "examples/kstar_EFIT01_35582_010000.esy_headerMod.geqdsk"
    eq_data = parse_geqdsk(geqdsk_path)
    return eq_data['limiter']


def test_mesh_size_0_01(limiter_boundary):
    """Test mesh size 0.01 completes quickly."""
    mesher = ContourMesher()

    start = time.time()
    vertices, elements = mesher.generate_mesh(
        limiter_boundary,
        target_element_size=0.01
    )
    elapsed = time.time() - start

    assert elapsed < 5.0, f"Too slow: {elapsed:.2f}s"
    assert len(vertices) > 5000
    assert len(elements) > 10000
    print(f"0.01: {elapsed:.2f}s, {len(vertices)} vertices, {len(elements)} triangles")


def test_mesh_size_0_005(limiter_boundary):
    """Test mesh size 0.005 completes in reasonable time."""
    mesher = ContourMesher()

    start = time.time()
    vertices, elements = mesher.generate_mesh(
        limiter_boundary,
        target_element_size=0.005
    )
    elapsed = time.time() - start

    assert elapsed < 10.0, f"Too slow: {elapsed:.2f}s"
    assert len(vertices) > 20000
    assert len(elements) > 40000
    print(f"0.005: {elapsed:.2f}s, {len(vertices)} vertices, {len(elements)} triangles")


def test_mesh_size_0_002(limiter_boundary):
    """Test mesh size 0.002 works (though slower)."""
    mesher = ContourMesher()

    start = time.time()
    vertices, elements = mesher.generate_mesh(
        limiter_boundary,
        target_element_size=0.002
    )
    elapsed = time.time() - start

    assert elapsed < 30.0, f"Too slow: {elapsed:.2f}s"
    assert len(vertices) > 100000
    assert len(elements) > 200000
    print(f"0.002: {elapsed:.2f}s, {len(vertices)} vertices, {len(elements)} triangles")


@pytest.mark.slow
def test_mesh_size_0_001(limiter_boundary):
    """
    Test mesh size 0.001 works (very slow, marked as slow test).

    This is the finest mesh size requirement from the user.
    Generates over 1 million triangles.
    """
    mesher = ContourMesher()

    start = time.time()
    vertices, elements = mesher.generate_mesh(
        limiter_boundary,
        target_element_size=0.001
    )
    elapsed = time.time() - start

    assert elapsed < 60.0, f"Too slow: {elapsed:.2f}s"
    assert len(vertices) > 500000
    assert len(elements) > 1000000
    print(f"0.001: {elapsed:.2f}s, {len(vertices)} vertices, {len(elements)} triangles")


def test_closed_boundary_handling():
    """
    Test that closed boundaries (first point == last point) are handled correctly.

    This is a regression test for the bug where duplicate closing points
    caused zero-length line segments and Gmsh to hang.
    """
    # Create a closed square boundary
    boundary_closed = np.array([
        [1.0, 1.0],
        [2.0, 1.0],
        [2.0, 2.0],
        [1.0, 2.0],
        [1.0, 1.0]  # Duplicate closing point
    ])

    mesher = ContourMesher()

    # This should complete quickly
    start = time.time()
    vertices, elements = mesher.generate_mesh(boundary_closed, target_element_size=0.1)
    elapsed = time.time() - start

    assert elapsed < 1.0, f"Should be fast, took {elapsed:.2f}s"
    assert len(vertices) > 0
    assert len(elements) > 0


def test_open_boundary_handling():
    """Test that open boundaries (first != last) also work."""
    # Create an open square boundary
    boundary_open = np.array([
        [1.0, 1.0],
        [2.0, 1.0],
        [2.0, 2.0],
        [1.0, 2.0]
        # No duplicate closing point
    ])

    mesher = ContourMesher()

    # This should also complete quickly
    start = time.time()
    vertices, elements = mesher.generate_mesh(boundary_open, target_element_size=0.1)
    elapsed = time.time() - start

    assert elapsed < 1.0, f"Should be fast, took {elapsed:.2f}s"
    assert len(vertices) > 0
    assert len(elements) > 0
