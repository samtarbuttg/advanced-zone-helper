"""Test ring zone detection end-to-end."""

import sys
sys.path.insert(0, '.')

from src.geometry import LineSegment, Arc, Circle, Loop, SimpleZone, RingZone
from src.geometry.arc_approximator import ArcApproximator
from src.geometry.loop_detector import LoopDetector
from src.geometry.ring_finder import RingFinder

# Create primitives similar to what KiCAD would produce:
# - A rectangle made of 4 line segments
# - A circle inside the rectangle

# Rectangle: centered at (150, 100), size 100x100
# Corners at (100, 50), (200, 50), (200, 150), (100, 150)
rect_segments = [
    LineSegment((100, 50), (200, 50)),   # top edge
    LineSegment((200, 50), (200, 150)),  # right edge
    LineSegment((200, 150), (100, 150)), # bottom edge
    LineSegment((100, 150), (100, 50)),  # left edge
]

# Circle: center at (150, 100), radius 30
circle = Circle((150, 100), 30)

print("=" * 60)
print("Input primitives:")
print("=" * 60)
for seg in rect_segments:
    print(f"  LineSegment: {seg.start} -> {seg.end}")
print(f"  Circle: center={circle.center}, radius={circle.radius}")

# Detect loops
print("\n" + "=" * 60)
print("Detecting loops:")
print("=" * 60)
all_primitives = rect_segments + [circle]
detector = LoopDetector(all_primitives)
loops = detector.detect_loops()

print(f"Found {len(loops)} loops:")
for i, loop in enumerate(loops):
    print(f"  Loop {i}: {len(loop.primitives)} primitives, closed={loop.is_closed}")
    for j, prim in enumerate(loop.primitives):
        if isinstance(prim, Circle):
            print(f"    {j}: Circle center={prim.center}, r={prim.radius}")
        elif isinstance(prim, LineSegment):
            print(f"    {j}: Line {prim.start} -> {prim.end}")

# Find ring zones
print("\n" + "=" * 60)
print("Finding zones (simple and ring):")
print("=" * 60)
arc_approx = ArcApproximator(segments_per_360=32)
finder = RingFinder(loops, arc_approx)
simple_zones, ring_zones = finder.find_zones()

print(f"\nResult: {len(simple_zones)} simple zones, {len(ring_zones)} ring zones")

for i, sz in enumerate(simple_zones):
    print(f"  Simple Zone {i+1}: {len(sz.loop.primitives)} primitives")
    
for i, rz in enumerate(ring_zones):
    print(f"  Ring Zone {i+1}: outer={len(rz.outer_loop.primitives)}, inner={len(rz.inner_loop.primitives)}")

if len(ring_zones) == 0:
    print("\n*** ERROR: Expected 1 ring zone but found none! ***")
else:
    print("\n*** SUCCESS: Ring zone detected correctly! ***")
