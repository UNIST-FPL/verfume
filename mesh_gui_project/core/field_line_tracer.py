"""
3D magnetic field line tracing with poloidal projection.

Traces field lines through toroidal angle steps and projects back to R-Z plane
for mesh vertex generation on flux surfaces.
"""
import numpy as np
from scipy.integrate import solve_ivp
from mesh_gui_project.core.magnetic_field import MagneticFieldCalculator


class FieldLineTracer:
    """
    Traces 3D magnetic field lines and projects to poloidal plane.

    Uses field line equation: dx/ds = B/|B|
    where x = (R, phi, Z) in cylindrical coordinates.
    """

    def __init__(self, equilibrium, n_toroidal_steps=64):
        """
        Initialize the field line tracer.

        Args:
            equilibrium: EquilibriumData object
            n_toroidal_steps: Number of toroidal steps (default 64)
        """
        self.equilibrium = equilibrium
        self.n_toroidal_steps = n_toroidal_steps
        self.B_calculator = MagneticFieldCalculator(equilibrium)

    def field_line_rhs(self, s, state, fpol_interp):
        """
        Right-hand side of field line ODE: dx/ds = B/|B|.

        Args:
            s: Arc length parameter
            state: [R, phi, Z] current position
            fpol_interp: Interpolator for poloidal current I(psi)

        Returns:
            [dR/ds, dphi/ds, dZ/ds]
        """
        R, phi, Z = state

        # Get psi at current location
        psi = self.equilibrium._interpolator.psi(R, Z, warn_extrapolate=False)

        # Get I value from fpol (interpolate based on psi or use fixed value)
        # For simplicity, use a representative I value
        # In real implementation, would interpolate fpol(psi)
        if fpol_interp is not None:
            I = fpol_interp(psi)
        else:
            # Default: use fpol at axis
            if hasattr(self.equilibrium, 'fpol') and self.equilibrium.fpol is not None:
                I = self.equilibrium.fpol[0]
            else:
                I = 1.0e6  # Default 1 MA

        # Compute magnetic field components
        B_R, B_Z, B_phi = self.B_calculator.compute_B_vector(R, Z, I)

        # Magnitude
        B_mag = np.sqrt(B_R**2 + B_Z**2 + B_phi**2)

        if B_mag < 1e-10:
            # Avoid division by zero
            return [0.0, 0.0, 0.0]

        # Normalized field: dx/ds = B/|B|
        dR_ds = B_R / B_mag
        dphi_ds = B_phi / (R * B_mag)  # dphi/ds = B_phi / (R * |B|)
        dZ_ds = B_Z / B_mag

        return [dR_ds, dphi_ds, dZ_ds]

    def trace_field_line(self, R_start, Z_start, fpol_interp=None):
        """
        Trace field line through one full toroidal circuit.

        Args:
            R_start: Starting R coordinate
            Z_start: Starting Z coordinate
            fpol_interp: Optional interpolator for I(psi)

        Returns:
            points: List of (R, Z) tuples at each toroidal step
        """
        # Initial state: [R, phi, Z]
        state0 = [R_start, 0.0, Z_start]

        # Toroidal angles to sample
        phi_target = 2 * np.pi
        delta_phi = phi_target / self.n_toroidal_steps

        points = []
        points.append((R_start, Z_start))  # Starting point

        current_state = state0

        # Trace through toroidal steps
        for i in range(self.n_toroidal_steps):
            # Target phi for this step
            phi_next = (i + 1) * delta_phi

            # Event function: stop when phi reaches target
            def phi_event(s, state):
                return state[1] - phi_next

            phi_event.terminal = True
            phi_event.direction = 1

            # Integrate until phi reaches target
            # Use a reasonable s_span (arc length)
            s_span = (0, 10.0)  # Max 10 meters arc length per step

            sol = solve_ivp(
                lambda s, y: self.field_line_rhs(s, y, fpol_interp),
                s_span,
                current_state,
                events=phi_event,
                dense_output=True,
                max_step=0.01
            )

            if sol.success and len(sol.t_events[0]) > 0:
                # Extract state at phi_next
                s_event = sol.t_events[0][0]
                state_event = sol.sol(s_event)

                R_new, phi_new, Z_new = state_event

                # Project to R-Z plane
                points.append((R_new, Z_new))

                # Update current state for next step
                current_state = [R_new, phi_new, Z_new]
            else:
                # Integration failed, use last known position
                points.append((current_state[0], current_state[2]))

        return points

    def generate_mesh_vertices_on_contour(self, psi_value, n_starting_points=None):
        """
        Generate mesh vertices on a PSI contour using field line tracing.

        Args:
            psi_value: PSI value of contour
            n_starting_points: Number of starting points around contour (default: n_toroidal_steps)

        Returns:
            vertices: np.ndarray (N, 2) of (R, Z) coordinates
        """
        if n_starting_points is None:
            n_starting_points = self.n_toroidal_steps

        # Extract contour polyline
        from mesh_gui_project.core.flux_surface import FluxSurfaceExtractor

        extractor = FluxSurfaceExtractor(self.equilibrium, n_rays=n_starting_points)

        psi_N = (psi_value - self.equilibrium.psi_axis) / \
                (self.equilibrium.psi_boundary - self.equilibrium.psi_axis)

        surfaces = extractor.extract_by_psiN([psi_N])

        if len(surfaces) == 0 or surfaces[0] is None:
            raise ValueError(f"Could not extract contour for psi={psi_value}")

        contour = surfaces[0]

        # Distribute starting points uniformly on contour
        n_contour_points = len(contour)
        indices = np.linspace(0, n_contour_points - 1, n_starting_points, dtype=int)
        starting_points = contour[indices]

        # Trace field lines from each starting point
        all_vertices = []

        for R_start, Z_start in starting_points:
            traced_points = self.trace_field_line(R_start, Z_start)

            # Add all traced points
            for R, Z in traced_points:
                all_vertices.append([R, Z])

        vertices = np.array(all_vertices)

        return vertices
