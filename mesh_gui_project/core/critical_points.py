"""
Critical points detection for magnetic equilibria.

Provides functions to find O-points (magnetic axis) and X-points (separatrices)
using gradient-based optimization.
"""
import numpy as np
from scipy.optimize import minimize, root
from typing import Tuple, List


def find_o_point(eq, eps: float = 1e-6) -> Tuple[float, float]:
    """
    Find O-point (magnetic axis) by refining the initial guess.

    Uses scipy.optimize.minimize to find the location where grad(psi) = 0
    and the Hessian has same-sign eigenvalues (extremum).

    Args:
        eq: EquilibriumData instance with attached interpolator
        eps: Convergence tolerance for gradient norm (default 1e-6)
            Note: For real equilibria with interpolation noise, a more
            relaxed tolerance (~1e-2) may be more appropriate.

    Returns:
        Tuple (R, Z) of O-point location

    Raises:
        RuntimeError: If optimization fails to converge or produce
                     a valid extremum
    """
    # Initial guess from equilibrium header
    R0 = eq.axis_R
    Z0 = eq.axis_Z

    # Objective function: minimize ||grad(psi)||^2
    def objective(x):
        R, Z = x
        grad_R, grad_Z = eq.grad_psi(R, Z)
        return grad_R**2 + grad_Z**2

    # Evaluate initial gradient norm to set adaptive tolerance
    grad_R0, grad_Z0 = eq.grad_psi(R0, Z0)
    initial_grad_norm = np.sqrt(grad_R0**2 + grad_Z0**2)

    # Use Nelder-Mead optimization (gradient-free, more robust for noisy data)
    # Try BFGS first for efficiency, fall back to Nelder-Mead if needed
    result = minimize(
        objective,
        x0=[R0, Z0],
        method='BFGS',
        options={'gtol': 1e-6}
    )

    R_o, Z_o = result.x
    grad_R, grad_Z = eq.grad_psi(R_o, Z_o)
    grad_norm = np.sqrt(grad_R**2 + grad_Z**2)

    # If BFGS didn't converge well, try Nelder-Mead
    if grad_norm > 1e-3:
        result = minimize(
            objective,
            x0=[R0, Z0],
            method='Nelder-Mead',
            options={'xatol': 1e-6, 'fatol': 1e-12}
        )
        R_o, Z_o = result.x
        grad_R, grad_Z = eq.grad_psi(R_o, Z_o)
        grad_norm = np.sqrt(grad_R**2 + grad_Z**2)

    # Use adaptive tolerance: either the specified eps, or require
    # at least 100x improvement over initial guess (for noisy real data)
    adaptive_eps = max(eps, initial_grad_norm * 1e-2)

    if grad_norm > adaptive_eps:
        raise RuntimeError(
            f"Could not find O-point: O-point gradient norm {grad_norm} "
            f"exceeds tolerance {adaptive_eps}"
        )

    # Verify it's an extremum (same sign eigenvalues)
    d2_dR2, d2_dZ2, d2_dRdZ = eq.hessian_psi(R_o, Z_o)

    # Determinant of Hessian matrix
    det = d2_dR2 * d2_dZ2 - d2_dRdZ**2

    if det < -1e-8:  # Allow small numerical errors
        raise RuntimeError(
            f"O-point has saddle Hessian (det={det} < 0), not an extremum"
        )

    return float(R_o), float(Z_o)


def find_x_points(eq, n_candidates: int = 20, eps: float = 1e-6) -> List[Tuple[float, float]]:
    """
    Find X-points (saddle points) in the equilibrium.

    Searches for candidates near psi_boundary where ||grad(psi)|| is locally
    minimal, then refines using root-finding on grad(psi) = 0. Validates
    saddle points by checking Hessian eigenvalues have opposite signs.

    Args:
        eq: EquilibriumData instance with attached interpolator
        n_candidates: Number of candidate locations to sample
        eps: Convergence tolerance for gradient norm

    Returns:
        List of (R, Z) tuples for found X-points (may be empty)
    """
    # Sample points near the boundary to find candidates
    # Use a ring of points around the plasma
    R_min, R_max = eq.R_grid[0], eq.R_grid[-1]
    Z_min, Z_max = eq.Z_grid[0], eq.Z_grid[-1]

    # Sample on a grid around the boundary
    n_r = int(np.sqrt(n_candidates))
    n_z = int(np.sqrt(n_candidates))

    R_samples = np.linspace(R_min, R_max, n_r)
    Z_samples = np.linspace(Z_min, Z_max, n_z)

    candidates = []

    # Find local minima of ||grad(psi)||
    # X-points can be anywhere, not just near boundary
    for R in R_samples:
        for Z in Z_samples:
            grad_R, grad_Z = eq.grad_psi(R, Z)
            grad_norm = np.sqrt(grad_R**2 + grad_Z**2)

            # If gradient is small, it's a candidate
            if grad_norm < 1.0:  # Threshold for candidates
                candidates.append((R, Z, grad_norm))

    # Sort candidates by gradient norm (smallest first)
    candidates.sort(key=lambda x: x[2])

    # Refine candidates using root-finding
    x_points = []
    found_locations = []  # For de-duplication

    for R0, Z0, _ in candidates:
        # Skip if too close to already found X-point
        too_close = False
        for R_prev, Z_prev in found_locations:
            dist = np.sqrt((R0 - R_prev)**2 + (Z0 - Z_prev)**2)
            if dist < 1e-5:  # Minimum separation (10 micrometers - matches xtol precision)
                too_close = True
                break

        if too_close:
            continue

        # Root-finding on grad(psi) = 0
        def gradient_system(x):
            R, Z = x
            grad_R, grad_Z = eq.grad_psi(R, Z)
            return [grad_R, grad_Z]

        try:
            # Use tighter tolerances for more accurate convergence
            result = root(
                gradient_system,
                x0=[R0, Z0],
                method='hybr',
                options={'xtol': 1e-8, 'maxfev': 2000}  # Tighter position tolerance, more iterations
            )

            if result.success:
                R_x, Z_x = result.x

                # Verify gradient is near zero with tighter tolerance
                grad_R, grad_Z = eq.grad_psi(R_x, Z_x)
                grad_norm = np.sqrt(grad_R**2 + grad_Z**2)

                if grad_norm > eps:
                    continue

                # Verify it's a saddle point (det < 0)
                d2_dR2, d2_dZ2, d2_dRdZ = eq.hessian_psi(R_x, Z_x)
                det = d2_dR2 * d2_dZ2 - d2_dRdZ**2

                # Saddle point has negative determinant
                # Use a threshold to handle numerical errors
                if det < 0:
                    # Check bounds
                    if R_min <= R_x <= R_max and Z_min <= Z_x <= Z_max:
                        # De-duplicate AFTER refinement - check if this refined point
                        # is too close to any already found refined X-point
                        is_duplicate = False
                        for R_prev, Z_prev in found_locations:
                            dist = np.sqrt((R_x - R_prev)**2 + (Z_x - Z_prev)**2)
                            if dist < 1e-5:  # 10 micrometer threshold (matches xtol precision)
                                is_duplicate = True
                                break

                        if not is_duplicate:
                            x_points.append((float(R_x), float(Z_x)))
                            found_locations.append((R_x, Z_x))

        except Exception:
            # Skip failed refinements
            continue

    return x_points
