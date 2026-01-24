"""Convert arcs and circles to polygon approximations."""

import math
import logging
from typing import List
from . import Arc, Circle, Bezier, Point

logger = logging.getLogger(__name__)


class ArcApproximator:
    """Approximates arcs and circles as polygons for zone creation."""

    def __init__(self, segments_per_360: int = 32):
        """Initialize approximator.

        Args:
            segments_per_360: Number of segments to use for a full 360° circle
        """
        self.segments_per_360 = max(4, segments_per_360)

    def approximate_arc(self, arc: Arc) -> List[Point]:
        """Approximate an arc as a series of line segments.

        Args:
            arc: Arc to approximate

        Returns:
            List of points along the arc (including start and end)
        """
        try:
            center, radius, start_angle, end_angle = arc.center_radius_angles()

            # Calculate arc angle - the end_angle is already normalized relative to start
            arc_angle = end_angle - start_angle
            
            # The arc should pass through the mid point. Check if going the calculated
            # direction actually passes through mid, otherwise go the other way.
            # This handles cases where the arc is > 180° vs < 180°
            mid_angle = math.atan2(arc.mid[1] - center[1], arc.mid[0] - center[0])
            
            # Normalize mid_angle relative to start_angle
            while mid_angle - start_angle > math.pi:
                mid_angle -= 2 * math.pi
            while mid_angle - start_angle < -math.pi:
                mid_angle += 2 * math.pi
            
            # Check if mid is between start and end when going arc_angle direction
            if arc_angle >= 0:
                # Going positive direction
                mid_in_range = 0 <= (mid_angle - start_angle) <= arc_angle
            else:
                # Going negative direction
                mid_in_range = arc_angle <= (mid_angle - start_angle) <= 0
            
            # If mid is not in range, we need to go the other way
            if not mid_in_range:
                if arc_angle > 0:
                    arc_angle = arc_angle - 2 * math.pi
                else:
                    arc_angle = arc_angle + 2 * math.pi

            # Calculate number of segments based on arc angle
            num_segments = max(2, int((abs(arc_angle) / (2 * math.pi)) * self.segments_per_360))

            # Generate points along arc
            points = []
            for i in range(num_segments + 1):
                t = i / num_segments
                angle = start_angle + t * arc_angle

                x = center[0] + radius * math.cos(angle)
                y = center[1] + radius * math.sin(angle)

                points.append((x, y))

            logger.debug(f"Approximated arc with {len(points)} points, arc_angle={math.degrees(arc_angle):.1f}°")
            return points

        except Exception as e:
            logger.error(f"Error approximating arc: {e}", exc_info=True)
            # Fallback: return start and end points
            return [arc.start, arc.end]

    def approximate_circle(self, circle: Circle) -> List[Point]:
        """Approximate a circle as a regular polygon.

        Args:
            circle: Circle to approximate

        Returns:
            List of points forming a closed polygon
        """
        try:
            num_segments = self.segments_per_360
            points = []

            for i in range(num_segments):
                angle = (i / num_segments) * 2 * math.pi

                x = circle.center[0] + circle.radius * math.cos(angle)
                y = circle.center[1] + circle.radius * math.sin(angle)

                points.append((x, y))

            logger.debug(f"Approximated circle with {len(points)} points")
            return points

        except Exception as e:
            logger.error(f"Error approximating circle: {e}", exc_info=True)
            return []

    def approximate_bezier(self, bezier: Bezier) -> List[Point]:
        """Approximate a cubic bezier curve as a series of line segments.

        Uses De Casteljau's algorithm to subdivide the curve.

        Args:
            bezier: Bezier curve to approximate

        Returns:
            List of points along the curve (including start and end)
        """
        try:
            # Use similar number of segments as arcs - estimate based on curve length
            # For bezier, use a fixed number of segments (can be refined later)
            num_segments = max(8, self.segments_per_360 // 4)

            p0 = bezier.start
            p1 = bezier.control1
            p2 = bezier.control2
            p3 = bezier.end

            points = []
            for i in range(num_segments + 1):
                t = i / num_segments
                
                # Cubic bezier formula: B(t) = (1-t)³P0 + 3(1-t)²tP1 + 3(1-t)t²P2 + t³P3
                u = 1 - t
                x = (u**3 * p0[0] + 
                     3 * u**2 * t * p1[0] + 
                     3 * u * t**2 * p2[0] + 
                     t**3 * p3[0])
                y = (u**3 * p0[1] + 
                     3 * u**2 * t * p1[1] + 
                     3 * u * t**2 * p2[1] + 
                     t**3 * p3[1])

                points.append((x, y))

            logger.debug(f"Approximated bezier with {len(points)} points")
            return points

        except Exception as e:
            logger.error(f"Error approximating bezier: {e}", exc_info=True)
            # Fallback: return start and end points
            return [bezier.start, bezier.end]

    def set_segments_per_360(self, segments: int):
        """Update the segments per 360 degrees setting.

        Args:
            segments: Number of segments (minimum 4)
        """
        self.segments_per_360 = max(4, segments)
        logger.debug(f"Arc approximation set to {self.segments_per_360} segments per 360°")
