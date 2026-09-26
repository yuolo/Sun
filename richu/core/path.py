"""Walkable polylines: the player moves along a scene's path."""
from __future__ import annotations

import math


class WalkPath:
    def __init__(self, points: list[tuple[int, int]]) -> None:
        if len(points) < 2:
            raise ValueError('a path needs at least two points')
        self.points = sorted(points)

    @property
    def x0(self) -> int:
        return self.points[0][0]

    @property
    def x1(self) -> int:
        return self.points[-1][0]

    def clamp(self, x: float) -> float:
        return max(self.x0, min(self.x1, x))

    def y_at(self, x: float) -> float:
        """Height of the path at x (the path is a function of x)."""
        x = self.clamp(x)
        pts = self.points
        for (ax, ay), (bx, by) in zip(pts, pts[1:]):
            if ax <= x <= bx:
                if bx == ax:
                    return ay
                t = (x - ax) / (bx - ax)
                return ay + (by - ay) * t
        return pts[-1][1]

    def nearest_x(self, x: float, y: float) -> float:
        """The path x closest to a clicked point."""
        best, best_d = self.clamp(x), math.inf
        for px in range(int(self.x0), int(self.x1) + 1, 2):
            d = (px - x) ** 2 + (self.y_at(px) - y) ** 2 * 0.5
            if d < best_d:
                best, best_d = px, d
        return best
