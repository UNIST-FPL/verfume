"""Test gEQDSK parser."""
import tempfile
from pathlib import Path
import numpy as np


def create_minimal_geqdsk_file():
    """Create a minimal valid gEQDSK file for testing.

    Follows the official gEQDSK format specification order:
    Line 6: fpol, Line 7: pres, Line 8: ffprim, Line 9: pprime,
    Line 10: psirz, Line 11: qpsi
    """
    NR = 5
    NZ = 5

    # Header line - use small grid 5x5 for testing
    content = f"  EFITD    09/29/2023    #000001   3000ms               3 {NR:3d} {NZ:3d}\n"

    # Line 2: Rdim, Zdim, Rcentr, Rleft, Zmid
    content += "   1.0000E+00   2.0000E+00   2.5000E+00   1.5000E+00   0.0000E+00\n"

    # Line 3: Rmag, Zmag, simag, sibry, Bcentr
    content += "   2.0000E+00   0.0000E+00   1.0000E+00  -0.5000E+00   2.5000E+00\n"

    # Line 4: Ip, simag, _, Rmag, _
    content += "   1.0000E+06   1.0000E+00   0.0000E+00   2.0000E+00   0.0000E+00\n"

    # Line 5: Zmag, _, sibry, _, _
    content += "   0.0000E+00   0.0000E+00  -0.5000E+00   0.0000E+00   0.0000E+00\n"

    # Line 6: Fpol array (NR values)
    for i in range(NR):
        content += f"   {2.5:.4E}"
        if (i + 1) % 5 == 0:
            content += "\n"
    if NR % 5 != 0:
        content += "\n"

    # Line 7: Pressure profile (NR values)
    for i in range(NR):
        content += f"   {0.1 * (1 - i / NR):.4E}"
        if (i + 1) % 5 == 0:
            content += "\n"
    if NR % 5 != 0:
        content += "\n"

    # Line 8: ffprime (NR values)
    for i in range(NR):
        content += "   0.0000E+00"
        if (i + 1) % 5 == 0:
            content += "\n"
    if NR % 5 != 0:
        content += "\n"

    # Line 9: pprime (NR values)
    for i in range(NR):
        content += "   0.0000E+00"
        if (i + 1) % 5 == 0:
            content += "\n"
    if NR % 5 != 0:
        content += "\n"

    # Line 10: Psi grid (NR * NZ values)
    for i in range(NR * NZ):
        content += f"   {i * 0.01:.4E}"
        if (i + 1) % 5 == 0:
            content += "\n"
    if (NR * NZ) % 5 != 0:
        content += "\n"

    # Line 11: qpsi (NR values)
    for i in range(NR):
        content += f"   {1.0 + 0.5 * i:.4E}"
        if (i + 1) % 5 == 0:
            content += "\n"
    if NR % 5 != 0:
        content += "\n"

    # Boundary and limiter
    content += "    5    8\n"  # NBDRY=5, NLIM=8

    # Boundary points (5 points)
    for i in range(5):
        r = 2.0 + 0.5 * np.cos(2 * np.pi * i / 5)
        z = 0.0 + 0.3 * np.sin(2 * np.pi * i / 5)
        content += f"   {r:.5E}   {z:.5E}\n"

    # Limiter points (8 points)
    for i in range(8):
        r = 1.5 + 1.0 * np.cos(2 * np.pi * i / 8)
        z = -1.0 + 2.0 * np.sin(2 * np.pi * i / 8)
        content += f"   {r:.5E}   {z:.5E}\n"

    return content


def test_geqdsk_parser_module_exists():
    """Test that geqdsk_parser module can be imported."""
    from mesh_gui_project.data import geqdsk_parser

    assert hasattr(geqdsk_parser, 'parse_geqdsk'), \
        "geqdsk_parser should have parse_geqdsk function"


def test_parse_geqdsk_returns_dict():
    """Test that parse_geqdsk returns a dictionary."""
    from mesh_gui_project.data.geqdsk_parser import parse_geqdsk

    # Create temporary gEQDSK file
    with tempfile.NamedTemporaryFile(mode='w', suffix='.geqdsk', delete=False) as f:
        f.write(create_minimal_geqdsk_file())
        temp_path = f.name

    try:
        result = parse_geqdsk(temp_path)
        assert isinstance(result, dict), "parse_geqdsk should return a dictionary"
    finally:
        Path(temp_path).unlink()


def test_parse_geqdsk_header_fields():
    """Test that parse_geqdsk extracts header fields correctly."""
    from mesh_gui_project.data.geqdsk_parser import parse_geqdsk

    with tempfile.NamedTemporaryFile(mode='w', suffix='.geqdsk', delete=False) as f:
        f.write(create_minimal_geqdsk_file())
        temp_path = f.name

    try:
        result = parse_geqdsk(temp_path)

        # Check required header fields
        assert 'nr' in result or 'NR' in result, "Should have NR field"
        assert 'nz' in result or 'NZ' in result, "Should have NZ field"
        assert 'rmag' in result or 'Rmag' in result, "Should have Rmag field"
        assert 'zmag' in result or 'Zmag' in result, "Should have Zmag field"
        assert 'psi_axis' in result or 'simag' in result, "Should have psi_axis field"
        assert 'psi_boundary' in result or 'sibry' in result, "Should have psi_boundary field"

    finally:
        Path(temp_path).unlink()


def test_parse_geqdsk_grid_dimensions():
    """Test that parse_geqdsk correctly identifies grid dimensions."""
    from mesh_gui_project.data.geqdsk_parser import parse_geqdsk

    with tempfile.NamedTemporaryFile(mode='w', suffix='.geqdsk', delete=False) as f:
        f.write(create_minimal_geqdsk_file())
        temp_path = f.name

    try:
        result = parse_geqdsk(temp_path)

        # The test file has 5x5 grid
        nr_key = 'nr' if 'nr' in result else 'NR'
        nz_key = 'nz' if 'nz' in result else 'NZ'

        # Header says 5x5
        assert result[nr_key] == 5, f"NR should be 5, got {result[nr_key]}"
        assert result[nz_key] == 5, f"NZ should be 5, got {result[nz_key]}"

    finally:
        Path(temp_path).unlink()


def test_parse_geqdsk_handles_scientific_notation():
    """Test that parser handles scientific notation correctly."""
    from mesh_gui_project.data.geqdsk_parser import parse_geqdsk

    with tempfile.NamedTemporaryFile(mode='w', suffix='.geqdsk', delete=False) as f:
        f.write(create_minimal_geqdsk_file())
        temp_path = f.name

    try:
        result = parse_geqdsk(temp_path)

        # Should successfully parse scientific notation values
        assert result is not None

    finally:
        Path(temp_path).unlink()


def test_parse_geqdsk_multiple_samples():
    """Test that parser works correctly with multiple gEQDSK samples (T11.1)."""
    from mesh_gui_project.data.geqdsk_parser import parse_geqdsk

    # Create multiple test files with different grid sizes
    test_configs = [
        {'NR': 5, 'NZ': 5},
        {'NR': 10, 'NZ': 10},
        {'NR': 7, 'NZ': 9},
    ]

    for config in test_configs:
        # Create gEQDSK file with specific dimensions
        NR = config['NR']
        NZ = config['NZ']

        content = f"  EFITD    09/29/2023    #000001   3000ms               3 {NR:3d} {NZ:3d}\n"
        content += "   1.0000E+00   2.0000E+00   2.5000E+00   1.5000E+00   0.0000E+00\n"
        content += "   2.0000E+00   0.0000E+00   1.0000E+00  -0.5000E+00   2.5000E+00\n"
        content += "   1.0000E+06   1.0000E+00   0.0000E+00   2.0000E+00   0.0000E+00\n"
        content += "   0.0000E+00   0.0000E+00  -0.5000E+00   0.0000E+00   0.0000E+00\n"

        # Line 6: Fpol array (NR values)
        for i in range(NR):
            content += f"   {2.5:.4E}"
            if (i + 1) % 5 == 0:
                content += "\n"
        if NR % 5 != 0:
            content += "\n"

        # Line 7: Pressure profile (NR values)
        for i in range(NR):
            content += f"   {0.1 * (1 - i / NR):.4E}"
            if (i + 1) % 5 == 0:
                content += "\n"
        if NR % 5 != 0:
            content += "\n"

        # Line 8: ffprime (NR values)
        for i in range(NR):
            content += "   0.0000E+00"
            if (i + 1) % 5 == 0:
                content += "\n"
        if NR % 5 != 0:
            content += "\n"

        # Line 9: pprime (NR values)
        for i in range(NR):
            content += "   0.0000E+00"
            if (i + 1) % 5 == 0:
                content += "\n"
        if NR % 5 != 0:
            content += "\n"

        # Line 10: Psi grid (NR * NZ values)
        for i in range(NR * NZ):
            content += f"   {i * 0.01:.4E}"
            if (i + 1) % 5 == 0:
                content += "\n"
        if (NR * NZ) % 5 != 0:
            content += "\n"

        # Line 11: qpsi (NR values)
        for i in range(NR):
            content += f"   {1.0 + 0.5 * i:.4E}"
            if (i + 1) % 5 == 0:
                content += "\n"
        if NR % 5 != 0:
            content += "\n"

        # Boundary and limiter
        content += "    5    8\n"

        # Boundary points (5 points)
        for i in range(5):
            r = 2.0 + 0.5 * np.cos(2 * np.pi * i / 5)
            z = 0.0 + 0.3 * np.sin(2 * np.pi * i / 5)
            content += f"   {r:.5E}   {z:.5E}\n"

        # Limiter points (8 points)
        for i in range(8):
            r = 1.5 + 1.0 * np.cos(2 * np.pi * i / 8)
            z = -1.0 + 2.0 * np.sin(2 * np.pi * i / 8)
            content += f"   {r:.5E}   {z:.5E}\n"

        with tempfile.NamedTemporaryFile(mode='w', suffix='.geqdsk', delete=False) as f:
            f.write(content)
            temp_path = f.name

        try:
            result = parse_geqdsk(temp_path)

            # Validate dimensions
            nr_key = 'nr' if 'nr' in result else 'NR'
            nz_key = 'nz' if 'nz' in result else 'NZ'

            assert result[nr_key] == NR, f"Expected NR={NR}, got {result[nr_key]}"
            assert result[nz_key] == NZ, f"Expected NZ={NZ}, got {result[nz_key]}"

        finally:
            Path(temp_path).unlink()


def test_geqdsk_correct_reading_order():
    """Test that parser reads arrays in correct order per gEQDSK spec.

    Official format order:
    Line 6: fpol(1:nw)
    Line 7: pres(1:nw)
    Line 8: ffprim(1:nw)
    Line 9: pprime(1:nw)
    Line 10: psirz(1:nw, 1:nh)
    Line 11: qpsi(1:nw)
    """
    from mesh_gui_project.data.geqdsk_parser import parse_geqdsk

    NR = 3
    NZ = 3

    # Build file in CORRECT official format order
    content = f"  TEST     01/01/2025    #000001   0ms                  3 {NR:3d} {NZ:3d}\n"

    # Line 2: Rdim, Zdim, Rcentr, Rleft, Zmid
    content += "   1.0000E+00   2.0000E+00   2.5000E+00   1.5000E+00   0.0000E+00\n"

    # Line 3: Rmag, Zmag, simag, sibry, Bcentr
    content += "   2.0000E+00   0.0000E+00   1.0000E+00  -0.5000E+00   2.5000E+00\n"

    # Line 4: Ip, simag, _, Rmag, _
    content += "   1.2345E+06   1.0000E+00   0.0000E+00   2.0000E+00   0.0000E+00\n"

    # Line 5: Zmag, _, sibry, _, _
    content += "   0.0000E+00   0.0000E+00  -0.5000E+00   0.0000E+00   0.0000E+00\n"

    # Line 6: fpol (NR values) - use distinctive values: 10, 11, 12
    content += "   1.0000E+01   1.1000E+01   1.2000E+01\n"

    # Line 7: pres (NR values) - use distinctive values: 20, 21, 22
    content += "   2.0000E+01   2.1000E+01   2.2000E+01\n"

    # Line 8: ffprim (NR values) - use distinctive values: 30, 31, 32
    content += "   3.0000E+01   3.1000E+01   3.2000E+01\n"

    # Line 9: pprime (NR values) - use distinctive values: 40, 41, 42
    content += "   4.0000E+01   4.1000E+01   4.2000E+01\n"

    # Line 10: psirz (NR*NZ = 9 values) - use distinctive values: 100-108
    content += "   1.0000E+02   1.0100E+02   1.0200E+02   1.0300E+02   1.0400E+02\n"
    content += "   1.0500E+02   1.0600E+02   1.0700E+02   1.0800E+02\n"

    # Line 11: qpsi (NR values) - use distinctive values: 50, 51, 52
    content += "   5.0000E+01   5.1000E+01   5.2000E+01\n"

    # Line 12: nbbbs, limitr
    content += "    0    0\n"

    with tempfile.NamedTemporaryFile(mode='w', suffix='.geqdsk', delete=False) as f:
        f.write(content)
        temp_path = f.name

    try:
        result = parse_geqdsk(temp_path)

        # Verify each array has correct values
        assert np.allclose(result['fpol'], [10.0, 11.0, 12.0]), \
            f"fpol should be [10, 11, 12], got {result['fpol']}"

        assert np.allclose(result['pres'], [20.0, 21.0, 22.0]), \
            f"pres should be [20, 21, 22], got {result['pres']}"

        assert np.allclose(result['ffprime'], [30.0, 31.0, 32.0]), \
            f"ffprime should be [30, 31, 32], got {result['ffprime']}"

        assert np.allclose(result['pprime'], [40.0, 41.0, 42.0]), \
            f"pprime should be [40, 41, 42], got {result['pprime']}"

        # psi_grid should be shaped (NZ, NR) with values 100-108
        expected_psi = np.array([100, 101, 102, 103, 104, 105, 106, 107, 108]).reshape(3, 3)
        assert np.allclose(result['psi_grid'], expected_psi), \
            f"psi_grid should be values 100-108 in 3x3, got {result['psi_grid']}"

        assert np.allclose(result['qpsi'], [50.0, 51.0, 52.0]), \
            f"qpsi should be [50, 51, 52], got {result['qpsi']}"

        # Verify plasma current is extracted
        assert 'Ip' in result or 'current' in result, "Should extract plasma current"
        ip_key = 'Ip' if 'Ip' in result else 'current'
        assert np.isclose(result[ip_key], 1.2345e6), \
            f"Plasma current should be 1.2345e6, got {result[ip_key]}"

    finally:
        Path(temp_path).unlink()


def test_parse_kstar_geqdsk_file():
    """Test parsing real KSTAR gEQDSK file with ffprime array."""
    from mesh_gui_project.data.geqdsk_parser import parse_geqdsk
    import os

    # Path to KSTAR file
    kstar_file = 'examples/kstar_EFIT01_35582_010000.esy_headerMod.geqdsk'

    # Skip if file doesn't exist
    if not os.path.exists(kstar_file):
        import pytest
        pytest.skip(f"KSTAR example file not found: {kstar_file}")

    # Parse the file
    result = parse_geqdsk(kstar_file)

    # Validate basic structure
    assert result['NR'] == 129, f"Expected NR=129, got {result['NR']}"
    assert result['NZ'] == 129, f"Expected NZ=129, got {result['NZ']}"

    # Validate psi_grid shape
    assert result['psi_grid'].shape == (129, 129), \
        f"Expected psi_grid shape (129, 129), got {result['psi_grid'].shape}"

    # Validate boundary and limiter data exist
    assert result['nbdry'] == 102, f"Expected nbdry=102, got {result['nbdry']}"
    assert result['nlim'] == 33, f"Expected nlim=33, got {result['nlim']}"
    assert result['boundary'] is not None, "Boundary should not be None"
    assert result['limiter'] is not None, "Limiter should not be None"
    assert len(result['boundary']) == 102, \
        f"Expected 102 boundary points, got {len(result['boundary'])}"
    assert len(result['limiter']) == 33, \
        f"Expected 33 limiter points, got {len(result['limiter'])}"

    # Validate ffprime array exists (new field)
    assert 'ffprime' in result, "Parser should include ffprime array"
    assert len(result['ffprime']) == 129, \
        f"Expected ffprime length 129, got {len(result['ffprime'])}"
