# SVG backend

Output is a single self-contained `.svg`, with its style and arrow markers
embedded. It opens in any browser and imports into slides, docs, wikis,
Figma, Inkscape and Illustrator. `scripts/render.py` makes a PNG, and any SVG
tool can make a PDF. No LaTeX is needed.

## Two ways to write it

**1. With `mlsvg.py` (preferred for anything with repetition or alignment).**
Write a short Python script. It computes positions from anchors, so stacks
stay centred and arrows land on borders.

```python
import sys; sys.path.insert(0, "<skill>/backends/svg")
from mlsvg import Figure, Box, union

f = Figure()
emb = f.block(150, 300, "Patch\nEmbedding", "embedding")   # centre x, centre y
att = f.above(emb, 30, "Self-Attention", "attention")       # 30 px gap
nrm = f.above(att, 4, "Add & Norm", "norm", h=16)           # thin block
f.arrow([emb.n, att.s])                                       # anchors: n s e w_ c nw ne sw se
f.connect(emb.n, nrm.w_, via="side", off=-50)                 # residual path
f.region(union(att, nrm, pad=10, pad_top=24), "encoder", "Encoder")
f.save("vit.svg", title="ViT block")
```

| call | draws |
|---|---|
| `block(cx, cy, label, role, w=80, h=32)` / `thin(...)` / `above(box, gap, ...)` | operator blocks |
| `neuron(cx, cy, role, r=14)` | neuron (roles: input, hidden, output, mean, variance, sample, or any hue) |
| `sum(cx, cy, "+")`, `circle(...)` | ⊕ nodes and plain circles |
| `tensor(x, y, cols, rows, role, cell=9.5, grid_role=None, hot=[(r, c)])` | gridded matrix, top-left anchored |
| `arrow(points)`, `path(points, cls, arrow)`, `connect(p, q, via="hv"/"vh"/"side")` | lines; `cls` can add `dashed`, `dotted`, `k-<hue>` |
| `edge(p, q)` | navy network edge with a white halo |
| `region(box, role, title, corner)`, `group(box)` | dotted tinted area, dashed group |
| `text(x, y, s, cls, anchor, size)` | text with `^{}`/`_{}`/`$italic$` markup and `\n` line breaks |
| `raw(svg, bbox, back=False)` | any hand-written SVG; pass its bbox so the canvas grows |

The canvas auto-fits everything drawn, plus 6 px of padding.

**2. By hand.** Copy a template `.svg` and keep its
`<!-- mlfig:begin --> … <!-- mlfig:end -->` block, which holds the CSS and
the arrow markers. Then use the classes below. Running
`python scripts/gen_styles.py` re-syncs that block in templates if tokens
change.

## CSS classes (from `mlfig.css`)

| class | effect |
|---|---|
| `blk` + `f-<name>` | block outline + block tint (`f-attention`, `f-norm`, `f-blue` ...) |
| `neuron fn-<name> s-<name>` | node tint + darkened outline |
| `region fr-<name>` / `group` | dotted region tint / dashed group outline |
| `cell f-<name>`, `grid`, `kl-<name>` | tensor cell, hairline grid, light hue stroke for grid lines |
| `fe-<name>` | emphasis tint (selected cell or token) |
| `line`, `edge`, `halo` | thin black line, navy network edge, white under-stroke |
| `arrow`, `arrow2`, `arrow-navy` | arrowhead at end, at both ends, navy head |
| `dashed`, `dotted` | line styles with meaning (see the style guide, section 4) |
| `t-<name>` | label text colour (hue 60% on black) |
| `k-<name>`, `c-<name>` | solid hue stroke / fill (thin lines, markers only) |
| `small`, `title`, `math`, `mono`, `start`, `end` | text size, weight, italic, mono, alignment |

`<name>` is any palette hue or semantic name from `tokens.yaml`.

## Gotchas
- Put `rx="2.4"` on block `<rect>`s as an attribute. Some renderers ignore
  `rx` set in CSS.
- `dominant-baseline: central` centres text vertically. For multi-line text
  use `<tspan x=… y=…>` per line (`mlsvg.text` does this).
- SVG has no LaTeX. Approximate math with italic tspans, `baseline-shift`
  sub/superscripts and Unicode (× · ⊕ ⊙ √ ∑ ∈ ≤ ⊤ ŷ). If a figure needs real
  typeset equations, prefer the TikZ backend.
- Fonts: the CSS asks for Latin Modern / CMU Serif and falls back to the
  system serif. For identical rendering on every machine, convert text to
  paths in Inkscape (`--export-text-to-path`) at the very end.
- Hand-written arrows: end the line exactly on the target border. The marker
  tip sits at the path end (`refX` = tip).
