"""Advanced Zone Helper - KiCAD Action Plugin (SWIG-based).

Creates zones from selected shapes, including ring zones (zones bounded by
two continuous loops like concentric circles).
"""

import pcbnew
import os
import sys
import logging
from pathlib import Path

# Add src directory to path
plugin_dir = Path(__file__).parent
sys.path.insert(0, str(plugin_dir))

# Configure logging
log_file = plugin_dir / "zone_helper.log"
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(log_file),
        logging.StreamHandler()
    ]
)

logger = logging.getLogger(__name__)


class AdvancedZoneHelper(pcbnew.ActionPlugin):
    """Action plugin for creating zones from selected shapes."""

    def defaults(self):
        self.name = "Advanced Zone Helper"
        self.category = "Zone Tools"
        self.description = "Create zones from selected shapes, including ring zones"
        self.show_toolbar_button = True
        icon_path = os.path.join(os.path.dirname(__file__), 'icons', 'advanced_zone_helper.png')
        if os.path.exists(icon_path):
            self.icon_file_name = icon_path

    def Run(self):
        """Main entry point when plugin is executed."""
        try:
            logger.info("=" * 60)
            logger.info("Advanced Zone Helper - Starting")
            logger.info("=" * 60)

            board = pcbnew.GetBoard()
            if not board:
                self._show_error("No board open")
                return

            # Import geometry modules
            from src.geometry.arc_approximator import ArcApproximator
            from src.geometry.shape_extractor_swig import ShapeExtractorSWIG
            from src.geometry.loop_detector import LoopDetector
            from src.geometry.ring_finder import RingFinder
            from src.zone_builder_swig import ZoneBuilderSWIG, ZoneSettings
            from src.config import DEFAULT_ARC_SEGMENTS

            # Extract shapes from selection
            extractor = ShapeExtractorSWIG(board)
            primitives = extractor.extract_from_selection()

            if not primitives:
                self._show_error("No valid shapes found in selection.\n\n"
                               "Please select graphic shapes (lines, arcs, circles) and try again.")
                return

            logger.info(f"Extracted {len(primitives)} primitives")

            # Detect loops
            detector = LoopDetector(primitives)
            loops = detector.detect_loops()

            if not loops:
                self._show_error("No closed loops found.\n\n"
                               "Please ensure selected shapes form complete closed loops.")
                return

            logger.info(f"Detected {len(loops)} loops")

            # Find zones (simple, ring, and multi-hole)
            arc_approximator = ArcApproximator(segments_per_360=DEFAULT_ARC_SEGMENTS)
            finder = RingFinder(loops, arc_approximator)
            simple_zones, ring_zones, multi_hole_zones = finder.find_zones()

            total_zones = len(simple_zones) + len(ring_zones) + len(multi_hole_zones)
            if total_zones == 0:
                self._show_error("No zones detected.")
                return

            logger.info(f"Found {len(simple_zones)} simple zones, {len(ring_zones)} ring zones, {len(multi_hole_zones)} multi-hole zones")

            # Show dialog to select zones and settings
            from src.ui.zone_dialog_swig import ZoneDialogSWIG
            
            dialog = ZoneDialogSWIG(simple_zones, ring_zones, multi_hole_zones, arc_approximator, board)
            result = dialog.ShowModal()
            
            if result == dialog.ID_OK:
                selected_zones = dialog.get_selected_zones()
                settings = dialog.get_settings()
                
                if selected_zones:
                    # Create zones
                    builder = ZoneBuilderSWIG(board, arc_approximator)
                    success_count = builder.create_zones(selected_zones, settings)
                    
                    pcbnew.Refresh()
                    
                    if success_count > 0:
                        self._show_info(f"Created {success_count} zone(s)")
                    else:
                        self._show_error("Failed to create zones. Check log for details.")
                else:
                    logger.info("No zones selected")
            else:
                logger.info("Dialog cancelled")
            
            dialog.Destroy()

            logger.info("Advanced Zone Helper - Complete")

        except Exception as e:
            logger.error(f"Error in Run: {e}", exc_info=True)
            self._show_error(f"Error: {str(e)}\n\nCheck log for details.")

    def _show_error(self, message):
        """Show error dialog."""
        import wx
        wx.MessageBox(message, "Advanced Zone Helper - Error", wx.OK | wx.ICON_ERROR)

    def _show_info(self, message):
        """Show info dialog."""
        import wx
        wx.MessageBox(message, "Advanced Zone Helper", wx.OK | wx.ICON_INFORMATION)


# Register the plugin when run directly (for testing)
# When imported as a package, __init__.py handles registration
if __name__ == "__main__" or __name__ == "zone_helper":
    AdvancedZoneHelper().register()
