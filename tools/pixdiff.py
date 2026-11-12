#!/usr/bin/env python3
# Compares two PNG files pixel by pixel: prints how many pixels differ and
# the box that holds them, and writes <b>.diff.png with the differences.
import sys
from PIL import Image, ImageChops

a = Image.open(sys.argv[1]).convert("RGBA")
b = Image.open(sys.argv[2]).convert("RGBA")
if a.size != b.size:
    print("sizes differ: %s %s" % (a.size, b.size))
    sys.exit(1)
d = ImageChops.difference(a, b)
box = d.getbbox()
if box is None:
    print("same")
    sys.exit(0)
n = sum(1 for p in d.getdata() if p != (0, 0, 0, 0))
d.convert("RGB").point(lambda v: 255 if v else 0).save(sys.argv[2][:-4] + ".diff.png")
print("%d pixels differ, in %s" % (n, box))
sys.exit(1)
