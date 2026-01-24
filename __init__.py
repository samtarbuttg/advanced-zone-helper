"""Advanced Zone Helper - KiCAD Action Plugin."""

from .zone_helper import AdvancedZoneHelper

# Register the plugin when this package is imported by KiCAD
AdvancedZoneHelper().register()
