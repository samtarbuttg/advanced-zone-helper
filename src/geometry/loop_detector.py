"""Detect closed loops in geometric primitives without external dependencies."""

import logging
import math
from typing import List, Dict, Set, Tuple
from . import LineSegment, Arc, Circle, Bezier, Loop, Point

logger = logging.getLogger(__name__)


class LoopDetector:
    """Detects closed loops from a collection of geometric primitives."""

    TOLERANCE = 0.01  # mm - increased for DXF import precision issues

    def __init__(self, primitives: List[LineSegment | Arc | Circle | Bezier]):
        """Initialize loop detector.

        Args:
            primitives: List of geometric primitives
        """
        self.primitives = primitives
        self.point_to_key: Dict[Point, str] = {}
        self.key_to_point: Dict[str, Point] = {}
        self.adjacency: Dict[str, List[Tuple[str, LineSegment | Arc | Bezier]]] = {}

    def detect_loops(self) -> List[Loop]:
        """Detect all closed loops from the primitives.

        Returns:
            List of Loop objects
        """
        loops = []

        try:
            # Handle circles separately (already closed)
            circles = [p for p in self.primitives if isinstance(p, Circle)]
            for circle in circles:
                loops.append(Loop([circle], is_closed=True))
                logger.debug(f"Found circle loop at {circle.center}")

            # Build adjacency from non-circle primitives
            non_circle_primitives = [p for p in self.primitives if not isinstance(p, Circle)]
            if not non_circle_primitives:
                return loops

            self._build_adjacency(non_circle_primitives)

            # Find cycles using DFS
            cycles = self._find_cycles_dfs()

            # Convert cycles to loops
            for cycle in cycles:
                loop = self._cycle_to_loop(cycle)
                if loop and loop.is_closed:
                    loops.append(loop)
                    logger.debug(f"Found loop with {len(loop.primitives)} primitives")

            logger.info(f"Detected {len(loops)} total loops")

        except Exception as e:
            logger.error(f"Error detecting loops: {e}", exc_info=True)

        return loops

    def _build_adjacency(self, primitives: List[LineSegment | Arc | Bezier]):
        """Build adjacency list from primitives."""
        for primitive in primitives:
            endpoints = primitive.endpoints()
            if len(endpoints) != 2:
                continue

            key_start = self._get_or_create_key(endpoints[0])
            key_end = self._get_or_create_key(endpoints[1])

            # Add bidirectional edges
            if key_start not in self.adjacency:
                self.adjacency[key_start] = []
            if key_end not in self.adjacency:
                self.adjacency[key_end] = []

            self.adjacency[key_start].append((key_end, primitive))
            self.adjacency[key_end].append((key_start, primitive))

        logger.debug(f"Built adjacency with {len(self.adjacency)} nodes")

    def _get_or_create_key(self, point: Point) -> str:
        """Get or create a unique key for a point."""
        for existing_point, key in self.point_to_key.items():
            if self._points_equal(point, existing_point):
                return key

        key = f"p{len(self.point_to_key)}"
        self.point_to_key[point] = key
        self.key_to_point[key] = point
        return key

    def _points_equal(self, p1: Point, p2: Point) -> bool:
        """Check if two points are equal within tolerance."""
        dx = p1[0] - p2[0]
        dy = p1[1] - p2[1]
        return math.sqrt(dx * dx + dy * dy) <= self.TOLERANCE

    def _find_cycles_dfs(self) -> List[List[Tuple[str, LineSegment | Arc | Bezier]]]:
        """Find all simple cycles using DFS.

        Returns:
            List of cycles, where each cycle is list of (node_key, primitive) tuples
        """
        cycles = []
        visited_edges: Set[Tuple[str, str]] = set()

        for start_node in self.adjacency:
            # DFS from each node
            found = self._dfs_find_cycle(start_node, visited_edges)
            if found:
                cycles.append(found)

        # Deduplicate
        unique_cycles = self._deduplicate_cycles(cycles)
        logger.debug(f"Found {len(unique_cycles)} unique cycles")
        return unique_cycles

    def _dfs_find_cycle(self, start: str, visited_edges: Set[Tuple[str, str]]) -> List[Tuple[str, LineSegment | Arc | Bezier]] | None:
        """Find a cycle starting from a node using DFS.

        Returns:
            Cycle as list of (node, primitive) tuples, or None
        """
        # Stack: (current_node, path, visited_in_path)
        stack = [(start, [], set())]

        while stack:
            current, path, visited_in_path = stack.pop()

            for next_node, primitive in self.adjacency.get(current, []):
                edge = tuple(sorted([current, next_node]))

                # Skip if we just came from this edge
                if path and path[-1][1] is primitive:
                    continue

                # Found a cycle back to start
                if next_node == start and len(path) >= 2:
                    cycle = path + [(current, primitive)]
                    # Mark edges as visited
                    for i in range(len(cycle)):
                        n1 = cycle[i][0]
                        n2 = cycle[(i + 1) % len(cycle)][0]
                        visited_edges.add(tuple(sorted([n1, n2])))
                    return cycle

                # Continue DFS if not visited
                if next_node not in visited_in_path and edge not in visited_edges:
                    new_visited = visited_in_path | {current}
                    stack.append((next_node, path + [(current, primitive)], new_visited))

        return None

    def _deduplicate_cycles(self, cycles: List[List[Tuple[str, LineSegment | Arc | Bezier]]]) -> List[List[Tuple[str, LineSegment | Arc | Bezier]]]:
        """Remove duplicate cycles."""
        unique = []
        seen = set()

        for cycle in cycles:
            # Create a canonical representation
            nodes = [c[0] for c in cycle]
            min_idx = nodes.index(min(nodes))
            rotated = nodes[min_idx:] + nodes[:min_idx]

            # Try both directions
            key1 = tuple(rotated)
            key2 = tuple([rotated[0]] + list(reversed(rotated[1:])))

            if key1 not in seen and key2 not in seen:
                seen.add(key1)
                unique.append(cycle)

        return unique

    def _cycle_to_loop(self, cycle: List[Tuple[str, LineSegment | Arc | Bezier]]) -> Loop | None:
        """Convert cycle to Loop object."""
        try:
            primitives = []

            for i, (node_key, primitive) in enumerate(cycle):
                next_node_key = cycle[(i + 1) % len(cycle)][0]

                # Orient primitive correctly
                oriented = self._orient_primitive(primitive, node_key, next_node_key)
                primitives.append(oriented)

            loop = Loop(primitives)
            logger.debug(f"Created loop with {len(primitives)} primitives, is_closed={loop.is_closed}")
            return loop

        except Exception as e:
            logger.error(f"Error converting cycle to loop: {e}", exc_info=True)
            return None

    def _orient_primitive(self, primitive: LineSegment | Arc | Bezier,
                         start_key: str, end_key: str) -> LineSegment | Arc | Bezier:
        """Orient primitive to match desired direction."""
        endpoints = primitive.endpoints()
        if len(endpoints) != 2:
            return primitive

        start_point = self.key_to_point[start_key]

        # Check if already correctly oriented
        if self._points_equal(endpoints[0], start_point):
            return primitive

        # Reverse
        if isinstance(primitive, LineSegment):
            return LineSegment(primitive.end, primitive.start)
        elif isinstance(primitive, Arc):
            return Arc(primitive.end, primitive.mid, primitive.start)
        elif isinstance(primitive, Bezier):
            return Bezier(primitive.end, primitive.control2, primitive.control1, primitive.start)

        return primitive
