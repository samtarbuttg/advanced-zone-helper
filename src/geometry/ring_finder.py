"""Detect ring zones using polygon containment (no external dependencies)."""

import logging
import math
from typing import List, Tuple
from . import Loop, RingZone, MultiHoleZone, SimpleZone, LineSegment, Arc, Circle, Bezier, Point
from .arc_approximator import ArcApproximator

logger = logging.getLogger(__name__)


class RingFinder:
    """Finds ring zones (areas between nested loops) and simple zones."""

    def __init__(self, loops: List[Loop], arc_approximator: ArcApproximator):
        """Initialize ring finder.

        Args:
            loops: List of detected loops
            arc_approximator: Arc approximator for converting to polygons
        """
        self.loops = loops
        self.arc_approximator = arc_approximator
        self.polygons: List[Tuple[Loop, List[Point]]] = []

    def find_zones(self) -> Tuple[List[SimpleZone], List[RingZone], List[MultiHoleZone]]:
        """Find all zones (simple, ring, and multi-hole).

        Returns:
            Tuple of (simple_zones, ring_zones, multi_hole_zones)
        """
        simple_zones = []
        ring_zones = []
        multi_hole_zones = []

        try:
            # Convert all loops to point lists
            self._convert_loops_to_polygons()

            if not self.polygons:
                logger.warning("No valid polygons created from loops")
                return simple_zones, ring_zones, multi_hole_zones

            # Log polygon details for debugging
            for i, (loop, pts) in enumerate(self.polygons):
                area = self._polygon_area(pts)
                logger.info(f"Polygon {i}: {len(pts)} points, area={area:.2f} mm², "
                           f"primitives={len(loop.primitives)}")
                if pts:
                    logger.debug(f"  First point: {pts[0]}, Last point: {pts[-1]}")

            # Find containment relationships
            containment = self._build_containment_graph()
            logger.info(f"Containment graph: {containment}")

            # Find direct children for each polygon (holes that are directly inside)
            direct_children = self._find_direct_children(containment)
            logger.info(f"Direct children: {direct_children}")

            # Create zones based on containment
            for i, (outer_loop, outer_pts) in enumerate(self.polygons):
                children = direct_children[i]
                
                if len(children) == 0:
                    # No holes - will be a simple zone
                    pass
                elif len(children) == 1:
                    # Single hole - ring zone
                    inner_loop = self.polygons[children[0]][0]
                    ring_zone = RingZone(outer_loop, inner_loop)
                    ring_zones.append(ring_zone)
                    logger.debug(f"Found ring zone: outer {i}, inner {children[0]}")
                else:
                    # Multiple holes - multi-hole zone
                    inner_loops = [self.polygons[j][0] for j in children]
                    multi_hole_zone = MultiHoleZone(outer_loop, inner_loops)
                    multi_hole_zones.append(multi_hole_zone)
                    logger.debug(f"Found multi-hole zone: outer {i}, {len(children)} holes")

            # Every loop is available as a simple zone
            for i, (loop, pts) in enumerate(self.polygons):
                simple_zones.append(SimpleZone(loop))

            logger.info(f"Found {len(simple_zones)} simple, {len(ring_zones)} ring, {len(multi_hole_zones)} multi-hole zones")

        except Exception as e:
            logger.error(f"Error finding zones: {e}", exc_info=True)

        return simple_zones, ring_zones, multi_hole_zones

    def _find_direct_children(self, containment: List[List[int]]) -> List[List[int]]:
        """Find direct children (holes) for each polygon.
        
        A polygon j is a direct child of i if:
        - i contains j
        - No other polygon k exists where i contains k and k contains j
        """
        n = len(self.polygons)
        direct_children = [[] for _ in range(n)]
        
        for i in range(n):
            for j in containment[i]:
                if self._is_direct_containment(i, j, containment):
                    direct_children[i].append(j)
        
        return direct_children

    def _convert_loops_to_polygons(self):
        """Convert all loops to point lists."""
        for loop in self.loops:
            try:
                points = self._loop_to_points(loop)
                if points and len(points) >= 3:
                    self.polygons.append((loop, points))
            except Exception as e:
                logger.error(f"Error converting loop: {e}", exc_info=True)

        logger.debug(f"Converted {len(self.polygons)} loops to polygons")

    def _loop_to_points(self, loop: Loop) -> List[Point]:
        """Convert a loop to a list of points."""
        points = []

        for primitive in loop.primitives:
            if isinstance(primitive, LineSegment):
                points.append(primitive.start)

            elif isinstance(primitive, Arc):
                arc_points = self.arc_approximator.approximate_arc(primitive)
                points.extend(arc_points[:-1])

            elif isinstance(primitive, Circle):
                circle_points = self.arc_approximator.approximate_circle(primitive)
                points.extend(circle_points)

            elif isinstance(primitive, Bezier):
                bezier_points = self.arc_approximator.approximate_bezier(primitive)
                points.extend(bezier_points[:-1])

        # Close the polygon
        if points and points[0] != points[-1]:
            points.append(points[0])

        return points

    def _point_in_polygon(self, point: Point, polygon: List[Point]) -> bool:
        """Check if point is inside polygon using ray casting.

        Args:
            point: Point to test
            polygon: List of polygon vertices

        Returns:
            True if point is inside
        """
        x, y = point
        n = len(polygon)
        inside = False

        j = n - 1
        for i in range(n):
            xi, yi = polygon[i]
            xj, yj = polygon[j]

            if ((yi > y) != (yj > y)) and (x < (xj - xi) * (y - yi) / (yj - yi) + xi):
                inside = not inside

            j = i

        return inside

    def _polygon_contains_polygon(self, outer: List[Point], inner: List[Point]) -> bool:
        """Check if outer polygon contains inner polygon.

        Args:
            outer: Outer polygon points
            inner: Inner polygon points

        Returns:
            True if all inner points are inside outer
        """
        logger.info(f"Checking containment: outer has {len(outer)} pts, inner has {len(inner)} pts")
        
        # Log first few points of each polygon for debugging
        if outer:
            logger.debug(f"  Outer first 3 pts: {outer[:3]}")
        if inner:
            logger.debug(f"  Inner first 3 pts: {inner[:3]}")
        
        # Check if all inner points are inside outer
        points_inside = 0
        points_outside = 0
        first_outside = None
        for point in inner[:-1]:  # Skip last (duplicate of first)
            is_inside = self._point_in_polygon(point, outer)
            if is_inside:
                points_inside += 1
            else:
                points_outside += 1
                if first_outside is None:
                    first_outside = point
                
        logger.info(f"  Inner points: {points_inside} inside, {points_outside} outside")
        if first_outside:
            logger.debug(f"  First outside point: {first_outside}")
        
        if points_outside > 0:
            return False

        # Reject if polygons are essentially identical (same area within tolerance)
        outer_area = self._polygon_area(outer)
        inner_area = self._polygon_area(inner)
        area_ratio = inner_area / outer_area if outer_area > 0 else 0
        logger.info(f"  Outer area: {outer_area:.2f}, Inner area: {inner_area:.2f}, ratio: {area_ratio:.3f}")
        
        if area_ratio > 0.99:
            logger.info(f"  Areas too similar - rejecting as same polygon")
            return False

        logger.info(f"  Containment confirmed!")
        return True

    def _polygon_centroid(self, polygon: List[Point]) -> Point:
        """Calculate polygon centroid."""
        n = len(polygon) - 1  # Exclude duplicate last point
        if n < 1:
            return polygon[0] if polygon else (0, 0)

        cx = sum(p[0] for p in polygon[:-1]) / n
        cy = sum(p[1] for p in polygon[:-1]) / n
        return (cx, cy)

    def _polygon_area(self, polygon: List[Point]) -> float:
        """Calculate polygon area using shoelace formula."""
        n = len(polygon)
        if n < 3:
            return 0.0

        area = 0.0
        for i in range(n - 1):
            j = (i + 1) % n
            area += polygon[i][0] * polygon[j][1]
            area -= polygon[j][0] * polygon[i][1]

        return abs(area) / 2.0

    def _build_containment_graph(self) -> List[List[int]]:
        """Build containment relationships between all polygons.

        Returns:
            Adjacency list where containment[i] = indices contained in i
        """
        n = len(self.polygons)
        containment = [[] for _ in range(n)]

        for i in range(n):
            for j in range(n):
                if i != j:
                    outer_pts = self.polygons[i][1]
                    inner_pts = self.polygons[j][1]

                    if self._polygon_contains_polygon(outer_pts, inner_pts):
                        containment[i].append(j)

        return containment

    def _is_direct_containment(self, outer_idx: int, inner_idx: int,
                              containment: List[List[int]]) -> bool:
        """Check if outer directly contains inner (no intermediate loops)."""
        for k in containment[outer_idx]:
            if k == inner_idx:
                continue
            if inner_idx in containment[k]:
                return False  # Found intermediate

        return True

    def calculate_area(self, loop: Loop) -> float:
        """Calculate the area of a loop in mm²."""
        points = self._loop_to_points(loop)
        return self._polygon_area(points)

    def calculate_ring_area(self, ring: RingZone) -> float:
        """Calculate the area of a ring zone in mm²."""
        outer_area = self.calculate_area(ring.outer_loop)
        inner_area = self.calculate_area(ring.inner_loop)
        return outer_area - inner_area
