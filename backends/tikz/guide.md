# TikZ backend

This backend gives the highest fidelity: true LaTeX typesetting, the same
fonts as a LaTeX document, and vector PDF. It needs a TeX distribution (TeX
Live / MiKTeX, with the standard `pgf` and `xcolor`).

## Setup

Put `mlfig.sty` where LaTeX can find it, next to the `.tex` file or on
`TEXINPUTS`. `scripts/render.py` adds the skill's copy automatically. Then:

```latex
\documentclass[border=2mm]{standalone}
\usepackage{mlfig}
\begin{document}
\begin{tikzpicture}[ml]
  ...
\end{tikzpicture}
\end{document}
```

The same `\usepackage{mlfig}` works in a full document. Use `\input` or
`\includegraphics` with the standalone PDF, whichever the document already
does.

## What `mlfig.sty` provides

**Colours:** `ml<hue>` for the palette (`mlblue`, `mlnavy` ...) and
`ml<concept>` for semantic names (`mlattention`, `mlquery`, `mlencoder` ...).
Mix them the usual xcolor way: `mlattention!15`, `mlred!30!black`.

**Styles:**

| style | use |
|---|---|
| `ml` | on the picture: font, arrowheads, inner sep 0, round joins |
| `op=<concept>` / `block=<hue>` | operator block (2 × 0.8 cm, 15% tint) |
| `thinblock=<concept>` | 0.4 cm high block (Add & Norm, Linear) |
| `neuron=<role>` | circle, 20% tint, outline hue!30!black |
| `edge`, `halo` | navy network edge; white under-stroke for crossings |
| `region=<concept>` | dotted, 10% tint background area (use on the background layer) |
| `group` | dashed outline for a repeated stack |
| `cell=<role>`, `hot=<role>` | tensor cell fill (20%) / emphasis fill (40%) |
| `tag=<role>` | coloured label text (hue 60% on black) |
| `title`, `note`, `sum` | bold region title, scriptsize note, ⊕ node |
| `w=`, `h=`, `s=` | minimum width / height / size shortcuts |

`\tensorgrid[<draw options>]{<node>}` draws grid lines inside a rectangular
node, aligned to its corner (cell `step=.25cm` by default).

## Idioms

- Position things relatively: `above=.1cm of att`, `right=1.5cm of enc`.
- Orthogonal routing: `\draw[->] (r1) -- ++(-1.25,0) |- (n1);`
- Branch points: `coordinate[pos=.6] (r1)` on the trunk arrow.
- Regions behind everything:
  `\begin{scope}[on background layer] \node[region=encoder, fit=...] {}; \end{scope}`
- `fit=` cannot parse `([shift]node)` coordinates. Define a `\coordinate`
  first and fit to that.
- Labels on nodes: `label={[tag=input, label distance=2mm]above:$X$}`.
- Dense layers: nested `\foreach`, with `halo` drawn before each `edge`.

## Export

`python scripts/render.py fig.tex` produces `fig.pdf` and `fig.png`. Adding
`--svg` also produces `fig.svg` via dvisvgm, for when a TikZ figure must go
somewhere that only takes SVG.
