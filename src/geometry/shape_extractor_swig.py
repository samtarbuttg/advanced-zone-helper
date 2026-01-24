"""Extract geometric shapes from KiCAD board selections using SWIG API (pcbnew)."""

import logging
import pcbnew
from typing import List
from . import LineSegment, Arc, Circle, Bezier, Point

logger = logging.getLogger(__name__)

# Conversion factor: KiCAD internal units (nm) to mm
IU_PER_MM = pcbnew.IU_PER_MM if hasattr(pcbnew, 'IU_PER_MM') else 1000000


def iu_to_mm(value) -> float:
    """Convert KiCAD internal units to millimeters."""
    return float(value) / IU_PER_MM


class ShapeExtractorSWIG:
    """Extract geometric primitives from board items using pcbnew SWIG API."""

    def __init__(self, board):
        """Initialize extractor with board reference.

        Args:
            board: pcbnew.BOARD object
        """
        self.board = board

    def extract_from_selection(self) -> List[LineSegment | Arc | Circle]:
        """Extract all geometric primitives from selected board items.

        Returns:
            List of geometric primitives (LineSegment, Arc, Circle)
        """
        primitives = []

        try:
            # Get selected items
            selected_items = self._get_selected_items()

            if not selected_items:
                logger.warning("No items selected")
                return primitives

            logger.info(f"Processing {len(selected_items)} selected items")

            for item in selected_items:
                item_primitives = self._extract_from_item(item)
                primitives.extend(item_primitives)

            logger.info(f"Extracted {len(primitives)} primitives from selection")

        except Exception as e:
            logger.error(f"Error extracting shapes from selection: {e}", exc_info=True)

        return primitives

    def _get_selected_items(self) -> list:
        """Get currently selected items from the board.

        Returns:
            List of selected board items
        """
        selected = []

        try:
            # Get all drawings and filter for selected ones
            for drawing in self.board.GetDrawings():
                if drawing.IsSelected():
                    selected.append(drawing)
                    logger.debug(f"Found selected: {type(drawing).__name__}")

        except Exception as e:
            logger.error(f"Error getting selected items: {e}", exc_info=True)

        logger.info(f"Found {len(selected)} selected items")
        return selected

    def _extract_from_item(self, item) -> List[LineSegment | Arc | Circle]:
        """Extract primitives from a single board item.

        Args:
            item: Board item (PCB_SHAPE)

        Returns:
            List of primitives extracted from this item
        """
        primitives = []

        try:
            # Get shape type
            shape_type = item.GetShape()
            type_name = self._shape_type_name(shape_type)
            logger.debug(f"Processing shape type: {type_name} ({shape_type})")

            if shape_type == pcbnew.SHAPE_T_SEGMENT:
                prim = self._extract_line_segment(item)
                if prim:
                    primitives.append(prim)

            elif shape_type == pcbnew.SHAPE_T_ARC:
                prim = self._extract_arc(item)
                if prim:
                    primitives.append(prim)

            elif shape_type == pcbnew.SHAPE_T_CIRCLE:
                prim = self._extract_circle(item)
                if prim:
                    primitives.append(prim)

            elif shape_type == pcbnew.SHAPE_T_RECT:
                rect_prims = self._extract_rectangle(item)
                primitives.extend(rect_prims)

            elif shape_type == pcbnew.SHAPE_T_POLY:
                poly_prims = self._extract_polygon(item)
                primitives.extend(poly_prims)

            elif hasattr(pcbnew, 'SHAPE_T_BEZIER') and shape_type == pcbnew.SHAPE_T_BEZIER:
                prim = self._extract_bezier(item)
                if prim:
                    primitives.append(prim)

            else:
                logger.warning(f"Unsupported shape type: {type_name}")

        except Exception as e:
            logger.error(f"Error extracting from item: {e}", exc_info=True)

        return primitives

    def _shape_type_name(self, shape_type) -> str:
        """Get human-readable name for shape type."""
        names = {
            pcbnew.SHAPE_T_SEGMENT: "SEGMENT",
            pcbnew.SHAPE_T_RECT: "RECT",
            pcbnew.SHAPE_T_ARC: "ARC",
            pcbnew.SHAPE_T_CIRCLE: "CIRCLE",
            pcbnew.SHAPE_T_POLY: "POLY",
        }
        # Handle SHAPE_T_BEZIER if it exists (added in newer versions)
        if hasattr(pcbnew, 'SHAPE_T_BEZIER'):
            names[pcbnew.SHAPE_T_BEZIER] = "BEZIER"
        return names.get(shape_type, f"UNKNOWN({shape_type})")

    def _extract_line_segment(self, item) -> LineSegment | None:
        """Extract line segment from PCB_SHAPE."""
        try:
            start = item.GetStart()
            end = item.GetEnd()

            start_mm = (iu_to_mm(start.x), iu_to_mm(start.y))
            end_mm = (iu_to_mm(end.x), iu_to_mm(end.y))

            logger.debug(f"  Line: {start_mm} -> {end_mm}")
            return LineSegment(start_mm, end_mm)

        except Exception as e:
            logger.error(f"Error extracting line segment: {e}", exc_info=True)
            return None

    def _extract_arc(self, item) -> Arc | None:
        """Extract arc from PCB_SHAPE."""
        try:
            start = item.GetStart()
            mid = item.GetArcMid()
            end = item.GetEnd()

            start_mm = (iu_to_mm(start.x), iu_to_mm(start.y))
            mid_mm = (iu_to_mm(mid.x), iu_to_mm(mid.y))
            end_mm = (iu_to_mm(end.x), iu_to_mm(end.y))

            logger.debug(f"  Arc: {start_mm} -> {mid_mm} -> {end_mm}")
            return Arc(start_mm, mid_mm, end_mm)

        except Exception as e:
            logger.error(f"Error extracting arc: {e}", exc_info=True)
            return None

    def _extract_circle(self, item) -> Circle | None:
        """Extract circle from PCB_SHAPE."""
        try:
            center = item.GetCenter()
            radius = item.GetRadius()

            center_mm = (iu_to_mm(center.x), iu_to_mm(center.y))
            radius_mm = iu_to_mm(radius)

            logger.debug(f"  Circle: center={center_mm}, radius={radius_mm}")
            return Circle(center_mm, radius_mm)

        except Exception as e:
            logger.error(f"Error extracting circle: {e}", exc_info=True)
            return None

    def _extract_rectangle(self, item) -> List[LineSegment]:
        """Extract rectangle as four line segments."""
        segments = []

        try:
            # Get corners
            start = item.GetStart()
            end = item.GetEnd()

            x1, y1 = iu_to_mm(start.x), iu_to_mm(start.y)
            x2, y2 = iu_to_mm(end.x), iu_to_mm(end.y)

            # Create four corners
            p1 = (x1, y1)  # top-left
            p2 = (x2, y1)  # top-right
            p3 = (x2, y2)  # bottom-right
            p4 = (x1, y2)  # bottom-left

            # Create segments (clockwise)
            segments.append(LineSegment(p1, p2))
            segments.append(LineSegment(p2, p3))
            segments.append(LineSegment(p3, p4))
            segments.append(LineSegment(p4, p1))

            logger.debug(f"  Rectangle: {p1} to {p3}")

        except Exception as e:
            logger.error(f"Error extracting rectangle: {e}", exc_info=True)

        return segments

    def _extract_polygon(self, item) -> List[LineSegment]:
        """Extract polygon as line segments."""
        segments = []

        try:
            # Get the polygon outline
            shape = item.GetPolyShape()
            if not shape or shape.OutlineCount() == 0:
                return segments

            outline = shape.Outline(0)
            point_count = outline.PointCount()

            if point_count < 2:
                return segments

            # Extract segments from polygon
            for i in range(point_count):
                p1 = outline.CPoint(i)
                p2 = outline.CPoint((i + 1) % point_count)

                start_mm = (iu_to_mm(p1.x), iu_to_mm(p1.y))
                end_mm = (iu_to_mm(p2.x), iu_to_mm(p2.y))

                segments.append(LineSegment(start_mm, end_mm))

            logger.debug(f"  Polygon: {point_count} points, {len(segments)} segments")

        except Exception as e:
            logger.error(f"Error extracting polygon: {e}", exc_info=True)

        return segments

    def _extract_bezier(self, item) -> Bezier | None:
        """Extract bezier curve from PCB_SHAPE."""
        try:
            start = item.GetStart()
            end = item.GetEnd()
            ctrl1 = item.GetBezierC1()
            ctrl2 = item.GetBezierC2()

            start_mm = (iu_to_mm(start.x), iu_to_mm(start.y))
            end_mm = (iu_to_mm(end.x), iu_to_mm(end.y))
            ctrl1_mm = (iu_to_mm(ctrl1.x), iu_to_mm(ctrl1.y))
            ctrl2_mm = (iu_to_mm(ctrl2.x), iu_to_mm(ctrl2.y))

            logger.debug(f"  Bezier: {start_mm} -> C1:{ctrl1_mm} -> C2:{ctrl2_mm} -> {end_mm}")
            return Bezier(start_mm, ctrl1_mm, ctrl2_mm, end_mm)

        except Exception as e:
            logger.error(f"Error extracting bezier: {e}", exc_info=True)
            return None
