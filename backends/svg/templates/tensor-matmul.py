"""Matrix arithmetic: gridded tensors whose shape shows dimensions, coloured by
role (x, query, key, value, weight). Run: python tensor-matmul.py"""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from mlsvg import Figure

f = Figure()
c = 9.5                     # cell size in px
for k, (role, sym) in enumerate([("query", "Q"), ("key", "K"), ("value", "V")]):
    y = 30 + k * 72
    x = f.tensor(10, y, 4, 2, "x", c)
    f.text(x.c[0], x.y - 12, "$X$", "t-x")
    w = f.tensor(x.x + x.w + 50, y - c, 3, 4, "weight", c, grid_role=role)
    f.text(w.c[0], w.y - 12, f"$W$^{{{sym}}}", f"t-{role}")
    out = f.tensor(w.x + w.w + 50, y, 3, 2, role, c)
    f.text(out.c[0], out.y - 12, f"${sym}$", f"t-{role}")
    f.text((x.x + x.w + w.x) / 2, x.c[1], "×", size=16)
    f.text((w.x + w.w + out.x) / 2, x.c[1], "=", size=16)

f.text(out.x + out.w + 40, 30 + 72 + c, "$Z$ = softmax( $Q$ $K$^{⊤} / √$d$_{k} ) $V$", anchor="start")

f.save(Path(__file__).with_suffix(".svg"), "QKV projections")
