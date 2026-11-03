"""Block diagram: operator stack with residual paths, a repeated group (N x)
and a tinted background region. Run: python block-diagram.py -> block-diagram.svg"""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from mlsvg import Figure, Box, union

f = Figure()
cx = 150

# Operators, bottom to top. A block and its norm sit 4px apart; stages 20-40px.
emb = f.block(cx, 356, "Token\nEmbedding", "embedding")
add = f.sum(cx, emb.y - 22)
pe = f.circle(add.x - 6 - 12, add.c[1], 11)
f.raw(f'<path class="line" d="M{pe.x + 2:g},{pe.c[1]:g} q4.5,-9 9,0 t9,0"/>')   # sine glyph
f.text(pe.x - 6, pe.c[1], "Positional\nEncoding", "small", anchor="end")

att = f.above(add, 52, "Multi-Head\nAttention", "attention")
n1 = f.above(att, 4, "Add & Norm", "norm", h=16)
ffn = f.above(n1, 22, "Feed\nForward", "mlp")
n2 = f.above(ffn, 4, "Add & Norm", "norm", h=16)

# Data flow
f.arrow([(cx, emb.y + emb.h + 20), emb.s]); f.text(cx, emb.y + emb.h + 30, "Inputs")
f.arrow([emb.n, add.s])
f.path([pe.e, add.w_], arrow=False)
r1 = (cx, add.y - 20)
r2 = (cx, (n1.y + ffn.y + ffn.h) / 2)
f.arrow([add.n, att.s])
f.arrow([n1.n, ffn.s])
f.arrow([n2.n, (cx, n2.y - 48)]); f.text(cx, n2.y - 58, "Outputs")

# Residual connections: leave the trunk, run alongside, re-enter the norm
f.connect(r1, n1.w_, via="side", off=-50)
f.connect(r2, n2.w_, via="side", off=-50)

# Repeated group and its multiplicity
stack = f.group(union(att, n2, pad=20))
times = f.text(stack.x - 6, stack.c[1], "N×", anchor="end")

# Background region with a reserved title strip
f.region(union(stack, times, Box(cx, r1[1], 0, 0), pad=8, pad_top=24), "encoder", "Encoder")

f.save(Path(__file__).with_suffix(".svg"), "Encoder block")
