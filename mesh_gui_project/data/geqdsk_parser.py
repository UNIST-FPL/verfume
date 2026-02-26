"""
gEQDSK file parser.

Parses EFIT equilibrium files in G-EQDSK format.
Units: SI (meters, Tesla, etc.)
"""
import numpy as np
from pathlib import Path


def parse_geqdsk(filepath):
    """
    Parse a gEQDSK file and return equilibrium data.

    Args:
        filepath: Path to the gEQDSK file

    Returns:
        dict: Dictionary containing equilibrium data with keys:
            - NR, NZ: Grid dimensions
            - Rdim, Zdim: Domain size in R and Z
            - Rleft, Zmid: Domain origin
            - Rmag, Zmag: Magnetic axis location
            - simag, sibry: Psi at axis and boundary
            - psi_axis, psi_boundary: Aliases for simag, sibry
            - Bcentr: Vacuum toroidal field at Rcentr
            - Rcentr: Reference R for toroidal field
            - Ip: Plasma current in Amperes
            - fpol: Poloidal current function F=RBt
            - psi_grid: 2D poloidal flux on grid (shape [NZ, NR])
            - qpsi: Safety factor q
            - pres: Plasma pressure
            - pprime: Pressure derivative
            - ffprime: F*dF/dpsi derivative
            - nbdry, nlim: Number of boundary and limiter points
            - boundary: Boundary points (Nx2 array)
            - limiter: Limiter points (Mx2 array)
    """
    filepath = Path(filepath)

    with open(filepath, 'r') as f:
        lines = f.readlines()

    # Parse header line
    # Format: case_id (48 chars), idum (4 int), NR, NZ
    header = lines[0]
    parts = header.split()
    NR = int(parts[-2])
    NZ = int(parts[-1])

    # Read second line: Rdim, Zdim, Rcentr, Rleft, Zmid
    line_idx = 1
    values = _read_floats(lines, line_idx, 5)
    Rdim, Zdim, Rcentr, Rleft, Zmid = values

    # Read third line: Rmag, Zmag, simag, sibry, Bcentr
    line_idx += _lines_needed(5)
    values = _read_floats(lines, line_idx, 5)
    Rmag, Zmag, simag, sibry, Bcentr = values

    # Read fourth line: Ip, simag (duplicate), _, Rmag (duplicate), _
    line_idx += _lines_needed(5)
    values = _read_floats(lines, line_idx, 5)
    Ip = values[0]  # Extract plasma current

    # Read fifth line: Zmag (duplicate), _, sibry (duplicate), _, _
    line_idx += _lines_needed(5)
    # Skip this line

    # Read arrays in CORRECT gEQDSK format order:
    # Line 6: fpol (NR values)
    line_idx += _lines_needed(5)
    fpol = _read_floats(lines, line_idx, NR)

    # Line 7: pres (NR values)
    line_idx += _lines_needed(NR)
    pres = _read_floats(lines, line_idx, NR)

    # Line 8: ffprime (NR values) - F*dF/dpsi
    line_idx += _lines_needed(NR)
    ffprime = _read_floats(lines, line_idx, NR)

    # Line 9: pprime (NR values)
    line_idx += _lines_needed(NR)
    pprime = _read_floats(lines, line_idx, NR)

    # Line 10: psi grid (NR * NZ values)
    # Note: gEQDSK stores psi in row-major order (by R, then Z)
    line_idx += _lines_needed(NR)
    psi_flat = _read_floats(lines, line_idx, NR * NZ)
    # Reshape to [NZ, NR] - C order means we read NR values per row
    psi_grid = np.array(psi_flat).reshape((NZ, NR), order='C')

    # Line 11: qpsi (NR values)
    line_idx += _lines_needed(NR * NZ)
    qpsi = _read_floats(lines, line_idx, NR)

    # Read NBDRY and NLIM
    line_idx += _lines_needed(NR)
    nbdry_nlim_line = lines[line_idx].strip()
    parts = nbdry_nlim_line.split()
    nbdry = int(parts[0])
    nlim = int(parts[1])

    # Read boundary points (nbdry pairs of R, Z)
    line_idx += 1
    boundary = None
    if nbdry > 0:
        boundary_flat = _read_floats(lines, line_idx, nbdry * 2)
        boundary = np.array(boundary_flat).reshape((nbdry, 2))
        line_idx += _lines_needed(nbdry * 2)

    # Read limiter points (nlim pairs of R, Z)
    limiter = None
    if nlim > 0:
        limiter_flat = _read_floats(lines, line_idx, nlim * 2)
        limiter = np.array(limiter_flat).reshape((nlim, 2))

    # Construct R_grid and Z_grid
    R_grid = np.linspace(Rleft, Rleft + Rdim, NR)
    Z_grid = np.linspace(Zmid - Zdim / 2, Zmid + Zdim / 2, NZ)

    return {
        'NR': NR,
        'NZ': NZ,
        'Rdim': Rdim,
        'Zdim': Zdim,
        'Rcentr': Rcentr,
        'Rleft': Rleft,
        'Zmid': Zmid,
        'Rmag': Rmag,
        'Zmag': Zmag,
        'simag': simag,
        'sibry': sibry,
        'psi_axis': simag,  # Alias for consistency
        'psi_boundary': sibry,  # Alias for consistency
        'Bcentr': Bcentr,
        'Ip': Ip,  # Plasma current (Amperes)
        'fpol': np.array(fpol),
        'psi_grid': psi_grid,
        'pres': np.array(pres),
        'pprime': np.array(pprime),
        'ffprime': np.array(ffprime),
        'qpsi': np.array(qpsi),
        'R_grid': R_grid,
        'Z_grid': Z_grid,
        'nbdry': nbdry,
        'nlim': nlim,
        'boundary': boundary,
        'limiter': limiter,
    }


def _read_floats(lines, start_line, count):
    """
    Read count floating-point values from lines starting at start_line.

    Handles scientific notation and line wrapping (typically 5 values per line).
    """
    import re
    values = []
    line_idx = start_line
    while len(values) < count and line_idx < len(lines):
        line = lines[line_idx].strip()
        if line:
            # Split on whitespace
            parts = line.split()
            for part in parts:
                if len(values) >= count:
                    break
                try:
                    values.append(float(part))
                except ValueError:
                    # Handle formats like "1.0E+001.0E+00" or "2.22e+00-1.17e-01" (no space)
                    # Split on 'e+' or 'e-' or 'E+' or 'E-' followed by digits and then another number
                    # Pattern: number with exponent, followed immediately by another number
                    pattern = r'([-+]?\d+\.?\d*[eE][-+]?\d+)'
                    matches = re.findall(pattern, part)
                    for match in matches:
                        if len(values) >= count:
                            break
                        try:
                            values.append(float(match))
                        except ValueError:
                            pass
        line_idx += 1

    return values


def _lines_needed(num_values, per_line=5):
    """Calculate number of lines needed for num_values at per_line values per line."""
    return (num_values + per_line - 1) // per_line
