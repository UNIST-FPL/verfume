"""
PSI Level Computer utility.

Computes PSI contour levels with filtering, eliminating duplication
across PSI handlers and controllers.
"""
import numpy as np
from typing import List, Union


class PsiLevelComputer:
    """Computes PSI contour levels with filtering."""

    @staticmethod
    def compute_levels(
        psi_grid: np.ndarray,
        added_values: Union[List[float], np.ndarray],
        disabled_levels: Union[List[float], np.ndarray],
        n_levels: int
    ) -> np.ndarray:
        """
        Compute filtered PSI contour levels.

        Combines automatic levels (evenly spaced across PSI range) with
        user-added values, then filters out disabled levels.

        Args:
            psi_grid: 2D PSI grid data
            added_values: User-added PSI values to include
            disabled_levels: PSI levels to exclude from output
            n_levels: Number of automatic levels to generate

        Returns:
            Sorted array of contour levels (may be empty if all disabled)
        """
        # Generate automatic levels evenly spaced across PSI range
        auto_levels = np.linspace(psi_grid.min(), psi_grid.max(), n_levels)

        # Combine with user-added values if any
        if len(added_values) > 0:
            all_levels = np.concatenate([auto_levels, added_values])
            # Remove duplicates and sort
            all_levels = np.unique(all_levels)
        else:
            all_levels = auto_levels

        # Filter out disabled levels
        available_levels = [level for level in all_levels
                           if level not in disabled_levels]

        return np.array(available_levels)
