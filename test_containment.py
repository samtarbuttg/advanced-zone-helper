"""Test containment detection."""

import math

def point_in_polygon(point, polygon):
    """Check if point is inside polygon using ray casting."""
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


def generate_circle_points(center, radius, segments=32):
    """Generate circle points."""
    points = []
    for i in range(segments):
        angle = (i / segments) * 2 * math.pi
        x = center[0] + radius * math.cos(angle)
        y = center[1] + radius * math.sin(angle)
        points.append((x, y))
    points.append(points[0])  # Close
    return points


def generate_square_points(center, size, clockwise=False):
    """Generate square points (4 corners)."""
    half = size / 2
    cx, cy = center
    if clockwise:
        # Clockwise (like KiCAD rectangle extraction)
        points = [
            (cx - half, cy - half),  # top-left
            (cx + half, cy - half),  # top-right
            (cx + half, cy + half),  # bottom-right
            (cx - half, cy + half),  # bottom-left
        ]
    else:
        # Counter-clockwise
        points = [
            (cx - half, cy - half),
            (cx - half, cy + half),
            (cx + half, cy + half),
            (cx + half, cy - half),
        ]
    points.append(points[0])  # Close
    return points


# Test: Circle inside square
# Square: 100x100 centered at (150, 100)
# Circle: radius 30 centered at (150, 100)

print("=" * 50)
print("Test with CCW square:")
print("=" * 50)
square = generate_square_points((150, 100), 100, clockwise=False)
circle = generate_circle_points((150, 100), 30, 32)

print(f"Square points ({len(square)}):")
for i, p in enumerate(square[:5]):
    print(f"  {i}: {p}")
    
print(f"\nCircle points ({len(circle)}):")
for i, p in enumerate(circle[:5]):
    print(f"  {i}: {p}")

# Check if circle points are inside square
print("\nChecking if circle points are inside square:")
inside_count = 0
outside_count = 0
for i, point in enumerate(circle[:-1]):  # Skip last (duplicate)
    is_inside = point_in_polygon(point, square)
    if is_inside:
        inside_count += 1
    else:
        outside_count += 1
        print(f"  Point {i} {point} is OUTSIDE!")

print(f"\nResult: {inside_count} inside, {outside_count} outside")

# Test with clockwise square
print("\n" + "=" * 50)
print("Test with CW square:")
print("=" * 50)
square_cw = generate_square_points((150, 100), 100, clockwise=True)
print(f"CW Square points: {square_cw}")

inside_count = 0
outside_count = 0
for point in circle[:-1]:
    if point_in_polygon(point, square_cw):
        inside_count += 1
    else:
        outside_count += 1
print(f"Circle in CW square: {inside_count} inside, {outside_count} outside")
