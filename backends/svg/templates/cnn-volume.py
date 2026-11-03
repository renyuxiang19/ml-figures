"""Convolutional pipeline: feature maps as oblique 3-D boxes (front width =
channels), a kernel with dotted projection lines. Run: python cnn-volume.py"""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from mlsvg import Figure, Box

f = Figure()


def volume(x, y, d, h, z, cls="line k-navy", fill="#FFFFFF"):
    """Front face top-left at (x, y): width d, height h; depth z recedes up-right.
    Feature maps: white with a navy edge. Kernels: light red edge, faint red fill."""
    ox, oy = 0.5 * z, -0.35 * z
    faces = [
        f"M{x:g},{y:g} h{d:g} v{h:g} h{-d:g} Z",                                   # front
        f"M{x + d:g},{y:g} l{ox:g},{oy:g} v{h:g} l{-ox:g},{-oy:g} Z",               # side
        f"M{x:g},{y:g} l{ox:g},{oy:g} h{d:g} l{-ox:g},{-oy:g} Z",                   # top
    ]
    f.raw("".join(f'<path class="{cls}" fill="{fill}" d="{p}"/>' for p in faces),
          Box(x, y + oy, d + ox, h - oy))
    return {"a": (x, y), "b": (x, y + h), "f": (x + ox, y + oy),
            "c": (x + d / 2 + ox / 2, y + h / 2 + oy / 2), "foot": (x, y + h)}


vin = volume(10, 60, 9, 120, 120)
k = volume(28, 92, 4.5, 30, 30, "line kl-red", "#FCF2F2")
c1 = volume(130, 75, 26, 90, 90)
c2 = volume(225, 90, 42, 52, 52)
fc = volume(325, 98, 9, 38, 9)

target = (c1["c"][0] - 12, c1["c"][1] - 6)
for corner in ("a", "b", "f"):
    f.path([k[corner], target], "line k-red dotted", arrow=False)

for v, t in [(vin, "Input\n224×224×3"), (c1, "Conv 1\n55×55×96"),
             (c2, "Conv 2\n27×27×256"), (fc, "FC\n4096")]:
    f.text(v["foot"][0], v["foot"][1] + 20, t, "small", anchor="start")

f.save(Path(__file__).with_suffix(".svg"), "CNN feature maps")
