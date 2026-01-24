"""Configuration settings for Advanced Zone Helper."""

# Default arc approximation (segments per 360 degrees)
DEFAULT_ARC_SEGMENTS = 32

# Point matching tolerance (mm)
POINT_TOLERANCE = 0.001

# Default zone settings
DEFAULT_LAYER = "F.Cu"
DEFAULT_CLEARANCE = 0.2  # mm
DEFAULT_MIN_THICKNESS = 0.1  # mm
DEFAULT_PRIORITY = 0

# UI settings
DIALOG_WIDTH = 900
DIALOG_HEIGHT = 700

# Preview colors (RGBA)
COLOR_ZONE_NORMAL = (200, 200, 200, 64)
COLOR_ZONE_SELECTED = (50, 200, 50, 128)
COLOR_ZONE_HIGHLIGHTED = (100, 150, 255, 128)
COLOR_STROKE_NORMAL = (100, 100, 100, 255)
COLOR_STROKE_SELECTED = (0, 150, 0, 255)
COLOR_STROKE_HIGHLIGHTED = (0, 100, 255, 255)
COLOR_HOLE = (255, 255, 255, 255)

# Logging
LOG_LEVEL = "DEBUG"
