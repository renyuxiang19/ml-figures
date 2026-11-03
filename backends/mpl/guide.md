# matplotlib backend

Use this backend for anything drawn from numbers: functions, training curves,
heatmaps, scatter, contours, histograms, bar charts. Plots then share
colours, fonts and line language with the diagrams.

## Setup

```python
import sys; sys.path.insert(0, "<skill>/backends/mpl")   # or copy mlfig.py,
import mlfig                                             # mlfig.mplstyle and
mlfig.use()                                              # mlfig_tokens.json
```

To make the style part of a user's own code, copy those three files into
their project. `mlfig.py` has no dependencies beyond matplotlib.

`use()` applies `mlfig.mplstyle` and registers the colormaps. If a TeX
distribution is present, it also registers Latin Modern so the text matches
LaTeX documents. Without one, matplotlib falls back to another serif, and
math still uses Computer Modern through `mathtext.fontset: cm`.

## API

| name | purpose |
|---|---|
| `C[name]` | base hex for any hue or semantic name (`C["blue2"]`, `C["attention"]`) |
| `tint(name, "block" \| "node" \| "region" \| "emphasis")` | the diagram tints, for fills (`fill_between`, bars, spans) |
| `shade(name, "outline" \| "label")` | darkened variants for edges and coloured text |
| `subplots(...)` | `plt.subplots` with the style applied and constrained layout |
| `origin_axes(ax, arrows=False, xlabel=, ylabel=)` | axes through (0, 0), textbook style |
| `end_labels(ax, x, ys, texts, colors)` | direct line labels, de-overlapped (call after limits are set) |
| `label_curve(ax, x, y, text, color)` | one direct label |
| `save(fig, stem, formats=("pdf", "svg", "png"))` | write the figure in several formats |
| colormaps `mlfig_seq`, `mlfig_div` (+ `_r`) | magnitudes / signed values |

## Recipes

- **Activation or loss function:** main curve in `C["blue2"]`, derivative in
  gray dashed `ls=(0, (4, 2))`, `origin_axes`, formula in a side panel. See
  `templates/function-plot.py`.
- **Training curves:** one hue per method, solid train and dashed
  validation, `end_labels` for the methods, and a legend for line style
  only. See `templates/training-curves.py`.
- **Attention map / confusion matrix:** `imshow(..., cmap="mlfig_seq")`,
  white minor grid, values in cells. See `templates/heatmap.py`.
- **Parameter space:** gray dashed contours, coloured constraint sets, bold
  annotations, axes with arrows. See `templates/contour-2d.py`.
- **Shaded uncertainty:** `fill_between(x, lo, hi, color=mlfig.tint(hue, "node"), lw=0)`
  under the line.
- **Bars:** fill `tint(hue, "node")`, edge `shade(hue, "outline")`, linewidth 0.8.

## Gotchas
- `lines.linewidth` is 2.2 for single-curve plots. With five or more series,
  pass `lw=1.4` to keep the plot calm.
- Ticks have zero length by design. If readers need precise values, add
  `ax.grid(True)` (a faint gray hairline is pre-styled) instead of tick marks.
- Keep the default `figsize` (4 × 2.8 in) unless the user specifies a size,
  so text stays at its intended size wherever the image is placed.
