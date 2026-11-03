"""Neuron graph: layers of circles, dense haloed connections, coloured layer
labels and a translucent group box. Run: python mlp-network.py"""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from mlsvg import Figure, union

f = Figure()
layers = [(4, "input"), (5, "hidden"), (5, "hidden"), (2, "output")]   # (size, role)
dx, dy, r = 95, 38, 14

nodes = []
for li, (n, role) in enumerate(layers):
    nodes.append([(60 + li * dx, 140 + (i - (n - 1) / 2) * dy) for i in range(n)])

# Edges first so neurons sit on top; the halo separates crossing lines.
for a, b in zip(nodes, nodes[1:]):
    for p in a:
        for q in b:
            f.edge(p, q)

boxes = [[f.neuron(x, y, role, r) for x, y in layer] for layer, (_, role) in zip(nodes, layers)]

# Translucent box around the output group, labelled below
g = union(*boxes[3], pad=5)

# Labels in the layer's darkened hue, clear of anything drawn around the layer
for li, name, top in [(0, "Input", boxes[0][0].y), (1, "Hidden", boxes[1][0].y), (3, "Output", g.y)]:
    f.text(boxes[li][0].c[0], top - 12, name, f"t-{layers[li][1]}")
f.raw(f'<rect class="fn-output s-output" opacity=".45" x="{g.x:g}" y="{g.y:g}" '
      f'width="{g.w:g}" height="{g.h:g}" stroke-width="0.8"/>', g, back=True)
f.text(g.c[0], g.y + g.h + 10, "$ŷ$", "t-output")

f.save(Path(__file__).with_suffix(".svg"), "MLP")
