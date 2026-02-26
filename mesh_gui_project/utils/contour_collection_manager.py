"""
Contour Collection Manager utility.

Manages matplotlib contour collections lifecycle, eliminating duplication
across PSI handlers and controllers.
"""
from matplotlib.axes import Axes
from typing import Dict


class ContourCollectionManager:
    """Manages matplotlib contour collections lifecycle."""

    def __init__(self, ax: Axes):
        """
        Initialize the ContourCollectionManager.

        Args:
            ax: Matplotlib axes object where contours are drawn
        """
        self.ax = ax
        self._tracked_collections: Dict[str, int] = {}

    def track_contour(self, name: str, collections_before: int):
        """
        Track collections created for a contour.

        Args:
            name: Identifier for the contour
            collections_before: Number of collections before contour was created
        """
        collections_after = len(self.ax.collections)
        count = collections_after - collections_before
        self._tracked_collections[name] = count

    def clear_contour(self, name: str):
        """
        Clear tracked contour collections.

        Args:
            name: Identifier for the contour to clear
        """
        if name in self._tracked_collections:
            count = self._tracked_collections[name]
            for _ in range(count):
                if len(self.ax.collections) > 0:
                    self.ax.collections[-1].remove()
            del self._tracked_collections[name]
