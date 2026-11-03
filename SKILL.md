---
name: ml-figures
description: Draw machine-learning and deep-learning figures in one consistent, textbook-quality visual style (pale semantic tints, thin dark lines, serif math labels), as SVG, TikZ/LaTeX or matplotlib. Use this whenever someone wants a figure, diagram, illustration or plot of anything ML - model architectures (Transformer, CNN, RNN/LSTM, VAE, GAN, diffusion U-Net, ViT, CLIP, MoE...), neural-network graphs, attention or tensor/matrix operations, training pipelines, data flow, loss landscapes, activation functions, training curves, attention heatmaps - even if they only say "draw", "visualise", "sketch", "make a figure of", "画图", "画个架构图", "示意图", or ask to restyle or redraw an existing ML figure so it looks consistent and clean.
---

# ML figures

This skill draws ML figures that look like they come from one carefully made
textbook. The look is pale semantic tints, thin dark outlines, serif text and
math italic, and the same colour for the same concept everywhere. The look
is defined once in `tokens.yaml`, and three backends render it:

| backend | output | best for |
|---|---|---|
| **SVG** (`backends/svg/`) | self-contained `.svg` (+ PNG) | diagrams that must open anywhere; no LaTeX needed |
| **TikZ** (`backends/tikz/`) | `.tex` → vector PDF (+ PNG/SVG) | diagrams that live in or next to LaTeX; real typeset maths |
| **matplotlib** (`backends/mpl/`) | `.py` → PDF/SVG/PNG | anything drawn from numbers or functions |

All paths below are relative to this skill's directory.

## Workflow

### 1. Understand the figure before choosing anything
Work out what the reader should understand from the figure: the components,
what flows between them, and what is repeated, optional or frozen. For a
known architecture, recall its actual structure (layer order, where the
residuals go, shapes) rather than a generic box chain. Sketch the layout in
your head: one flow direction, the stacks, the regions.

### 2. Pick the backend from evidence, not assumption
Don't guess what the figure is for (paper, slides, blog, README...). Choose
by what you can actually observe:

1. **The user named a format or tool** ("TikZ", "SVG", "PNG for my slides",
   "matplotlib"): use it.
2. **The figure is drawn from data or a mathematical function** (curves,
   heatmaps, scatter, contours): use **matplotlib**, whatever the
   destination.
3. **The surrounding project shows a toolchain.** A LaTeX project (`.tex`
   files, the user is editing a paper source) points to **TikZ**. A Python
   or notebook codebase that should generate the plot points to
   **matplotlib** inside their code.
4. **Otherwise, for diagrams: SVG.** It needs no toolchain, opens
   everywhere, and converts to PNG/PDF. In one sentence, mention that a TikZ
   version is available if they work in LaTeX.

If the user later asks for another format, port the figure. The style is
identical across backends, so this is a translation, not a redesign.

### 3. Apply the style
Read `references/style-guide.md` the first time in a session. It has the
colour semantics, shape vocabulary, line meanings and spacing; the parts
that matter most:
- Colour means concept: embedding red, attention orange, norm green, MLP
  blue, input green, output red, Q/K/V red/blue/cyan, and so on. Use the
  semantic names, which every backend accepts. Use at most four hues plus
  gray per figure.
- Fills are pale tints (10/15/20%), never solid hues. Lines are thin black
  (navy for network edges).
- Use a dotted tinted *region* for sub-systems, a dashed *group* plus `N×`
  for repeats, and dashed lines for optional or inference-only paths.
- Text is serif at footnote size, symbols are math italic, and coloured
  labels match their object. No sentences inside figures.

Then read the backend guide you chose: `backends/<svg|tikz|mpl>/guide.md`.
Start from the closest template in `backends/<backend>/templates/`; each one
has a `.png` preview next to it:
- `block-diagram` covers operator stacks with residuals, groups and regions.
- `mlp-network` covers neuron graphs.
- `tensor-matmul` covers matrices and QKV arithmetic.
- `cnn-volume` covers 3-D feature maps.
- The mpl templates are `function-plot`, `training-curves`, `heatmap` and
  `contour-2d`.

Adapt the template; don't rebuild the style by hand. If the figure is
nothing like any template, still use the style files (`mlsvg.py`,
`mlfig.sty`, `mlfig.py`), so tokens stay the single source of truth.

### 4. Render and look at it
```bash
python scripts/render.py <figure.svg | figure.tex | figure.py>
```
This writes a PNG (and a PDF for TikZ) and prints `WARN` lines for common
slips: unknown CSS classes, text outside the canvas, overfull boxes, missing
glyphs. **Open the PNG and inspect it** against the checklist at the end of
the style guide: no overlaps, arrows on borders, consistent sizes, at most
four hues. Fix and re-render until it is clean. Most first drafts have at
least one collision, so expect to iterate once or twice.

### 5. Deliver
Deliver the editable source (`.svg`, `.tex` + `mlfig.sty`, or `.py`) and the
rendered file(s). Say in a line which backend you used and why. If the
choice was a default and not something the user asked for, name the
alternative. For TikZ, deliver `mlfig.sty` too, or inline the few
definitions the figure uses if a single file must stand alone. For
matplotlib inside a user's codebase, copy `mlfig.py`, `mlfig.mplstyle` and
`mlfig_tokens.json` next to their code instead of pointing at the skill.

## Restyling an existing figure
When the user brings a figure (an image, a TikZ/SVG file, or a description
of a paper figure), keep its *content and topology* and replace its
*styling*. Keep the same components, connections and labels. Map its colours
to the semantic palette, and swap its shapes for this vocabulary. Point out
anything ambiguous in the original rather than inventing structure.

## Changing the look itself
Everything visual derives from `tokens.yaml`. To re-theme (for example to
another palette or a different line weight), edit it and run
`python scripts/gen_styles.py`. That regenerates `mlfig.sty`, `mlfig.css`,
`mlfig.mplstyle` and the style block inside every SVG template. Never edit
the generated files directly.
