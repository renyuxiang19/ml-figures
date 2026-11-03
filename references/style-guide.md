# mlfig style guide

This file describes the look. It applies to every backend. The exact numbers
live in `tokens.yaml`, and the generated style files apply them for you. This
guide covers the judgement calls that tokens can't encode.

## Contents
1. The look in one paragraph
2. Colour
3. Shape vocabulary
4. Lines and arrows
5. Text
6. Layout and spacing
7. Plots
8. Pre-delivery checklist

---

## 1. The look in one paragraph

The look is a textbook figure. Shapes are pale and lines are thin and dark.
The colour is low in saturation, but every colour means something. Blocks
have a light tint fill (15% of the hue), a thin black outline and slightly
rounded corners. Neurons have a 20% tint, with a thicker outline in the same
hue darkened to near-black. Large areas such as "Encoder" or "Decoder" get an
even paler 10% tint and a dotted border. Repeated sub-stacks get a dashed box
and an `N×` marker. Text is serif (Computer/Latin Modern) at footnote size,
and symbols are in math italic. There are no shadows, gradients or 3-D
effects, apart from oblique boxes for CNN volumes. The figure should still
read if printed in greyscale, because the tints differ in lightness as well
as hue.

## 2. Colour

### Palette
| name | hex | role |
|---|---|---|
| blue | `#0000CC` | default "computation" hue |
| blue2 | `#0000A3` | curves in plots |
| red | `#CC0000` | embeddings, gates, outputs, loss, highlights |
| green | `#009900` | inputs, normalisation, "good" |
| orange | `#E67300` | attention |
| yellow | `#E0E000` | means, heads (always used as a tint, never solid) |
| purple | `#660066` | latents, samples |
| cyan | `#0080E6` | values, encoder regions, pooling |
| navy | `#000066` | network edges, feature-map outlines |
| darkgreen | `#004D00` | softmax / output heads (10% tint) |
| gray | `#808080` | frozen, masked, unused, auxiliary curves |

Every hue appears in fixed derived forms. Use the form, not an ad-hoc mix.

| form | recipe | used for |
|---|---|---|
| region | hue 10% on white | large background areas |
| block | hue 15% | operator blocks |
| node | hue 20% | neurons, tensor cells, tokens |
| emphasis | hue 40% | the one selected cell or token |
| outline | hue 30% on black | neuron outlines |
| label | hue 60% on black | text that names a coloured object |
| solid | 100% | curves, thin projection lines, small markers only |

### Concept to colour
The same concept keeps the same colour everywhere, across figures as well as
within one. Use the semantic names in `tokens.yaml`; each backend accepts them
directly (`op=attention`, `f-attention`, `C["attention"]`).

- **Operators:** embedding = red, attention = orange, norm (Add & Norm, LayerNorm, BatchNorm) = green, MLP/FFN = blue, linear projection = navy at 10%, softmax/head = darkgreen at 10%, conv = blue, pool = cyan, recurrent cell = blue, gates = red, memory/cell state = gray, frozen/masked = gray, latent = purple.
- **Neuron layers:** input = green, hidden = blue, output = red, mean μ = yellow, variance σ = orange, sample z = purple.
- **Tensors:** X = green, Q = red, K = blue, V = cyan, weights = gray fill with grid lines in the role's hue.
- **Regions:** encoder = cyan, decoder = green, preprocessing = orange, head = yellow.

**Concepts not in the table.** Map a new concept to the nearest existing
role. For example, a LoRA adapter is a linear projection (navy), an MoE
router behaves like attention (orange), and a cross-attention block is
attention. If nothing fits, use a hue that isn't yet used in the figure
(purple, yellow, cyan, in that order). Then name the mapping in a legend or
caption-ready sentence so the reader can decode it.

**Restraint.** Use at most four hues plus gray in a single figure. If more
categories exist, group them: give the figure two levels of meaning (region
colour and block colour), not eight block colours.

## 3. Shape vocabulary

| shape | meaning | spec |
|---|---|---|
| block (rect, ~2 × 0.8 cm / 80 × 32 px, r ≈ 0.5 mm) | an operator or layer | block tint, thin black outline, label centred, 1–3 short lines |
| thin block (height 0.4 cm / 16 px) | a cheap op stacked onto a block: Add & Norm, Linear, Softmax | sits 0.1 cm / 4 px above the block it belongs to |
| neuron (circle, 22 pt / r = 14 px) | a unit in a neuron graph | node tint, thick outline in hue!30!black |
| sum node (small circle, 0.3 cm / r = 6 px) | ⊕ addition, ⊙ product, ‖ concat | white fill, thin outline, symbol inside |
| tensor grid | a matrix or sequence of vectors | node tint, 0.25 cm / 9.5 px cells, hairline grid; the aspect ratio shows the shape |
| token square | one token or patch in a sequence | small node-tint square, index or `[M]` inside; image patches as thumbnails |
| trapezium | an encoder/decoder that changes resolution (tokeniser, VAE encoder) | block tint; the wide side faces the larger representation |
| oblique box | a CNN feature map or volume | white fill, navy outline; front width = channels, depth = spatial size |
| region | a sub-system (Encoder, Decoder, Preprocessing) | region tint, dotted border, square corners, bold title in a free corner |
| group | a repeated stack or logical unit | dashed border, no fill, `N×` beside it |

Keep sizes consistent within a figure: all main blocks get one width, and all
thin blocks get the same width as the blocks they sit on.

## 4. Lines and arrows

- **Data flow:** use thin black lines with a filled Latex-style arrowhead
  (about 1.5 × 1.25 mm). The arrow ends exactly on the target's border.
- **Routing:** use orthogonal routing (`-|`, `|-`) for skips and residuals.
  The line leaves the trunk at a junction, runs parallel to the stack about
  1.25 cm / 50 px to the side, and re-enters the target from the side. Use
  straight diagonals only in neuron graphs and for "fan-in" into a single
  box.
- **Network edges** in neuron graphs are thicker and navy. Draw a white
  halo under each edge so that crossings stay legible.
- **Line styles carry meaning:**
  - solid: always happens.
  - densely dashed: optional, inference-only, or "not used during training".
  - densely dotted in a hue: a correspondence or projection (kernel to
    receptive field, token to embedding).
  - coloured dashed curve with an arrow: gather or select (masked tokens
    picked out to a head).
- **Gradient or backward flow** should be visually distinct from the forward
  pass. Use a red dashed line, a curved route, or both, and say so once in a
  label.
- Line joins are round. Avoid line crossings where a re-order removes them.

## 5. Text

- Font: Computer Modern / Latin Modern serif. In SVG, fall back to another
  serif, never to a sans-serif. Symbols use math italic (`$x_t$`, `W^Q`);
  operators and words are upright.
- Sizes: labels inside blocks are footnotesize (≈ 9 pt / 12 px). Secondary
  notes and dimensions are scriptsize (≈ 7.5 pt / 10 px). Region titles are
  bold at label size. Nothing is larger, apart from symbols like `×` / `=` in
  equations drawn between tensors (≈ 1.4×).
- Labels that name a coloured object take its *label* colour (hue 60% on
  black), for example a green "Input" over green neurons, or a red `Q` over
  a red tensor. All other text is black.
- Place input labels below or left of the input arrow's tail, and output
  labels above or right of the last arrow's tip. Put matrix names above the
  matrix, and side notes (Positional Encoding) left or right with about 1 mm
  of gap.
- Use title case for block names, keep them to 1–3 words per line, and break
  lines rather than widen blocks.
- Captions belong to the host document, not inside the figure. A figure may
  contain a bold region title, but never a sentence.

## 6. Layout and spacing

- Choose one primary direction of flow. Bottom-to-top is the Transformer
  convention. Left-to-right suits pipelines, CNNs, unrolled RNNs and
  sequence models. Mix the two only for nested detail, for example a
  left-to-right pipeline whose blocks are drawn bottom-to-top.
- Spacing, in TikZ cm and SVG px:
  - block to its thin block: 0.1 cm / 4 px.
  - consecutive stages: 0.5–1 cm / 20–40 px.
  - between parallel columns (encoder and decoder): 1.5 cm / 60 px.
  - region padding: 0.2–0.35 cm / 8–14 px, with an extra strip for the title.
- Align. Blocks in a stack share one centre line, and repeated rows share
  baselines. Position things relative to each other (TikZ `positioning`,
  mlsvg `above()`), not with absolute numbers sprinkled around.
- Leave white space. If a figure feels crowded, widen the stage gap before
  shrinking text.

## 7. Plots

- The main curve is thick (≈ 2.2 pt) in blue2. A derivative or reference
  curve is gray and dashed. Further series take red, green, orange, purple
  and cyan, in that order.
- Function plots draw their axes through the origin with no frame or tick
  marks, only a few tick labels. Data plots keep the left and bottom spines,
  again with no tick marks and no grid.
- Label lines directly at their ends when there are four or fewer. Use a
  legend for line *styles* (train vs validation), not for colours you could
  label directly.
- Heatmaps use `mlfig_seq` (white to blue to navy) for magnitudes and
  `mlfig_div` (red to white to blue) for signed values. Separate cells with
  white lines, and print values in cells when there are 100 or fewer cells.
- A formula that defines the plotted function goes beside the plot in the
  curve's colour, with a bold name above it.
- Annotations are bold black text with a thin arrow, placed in empty space.

## 8. Pre-delivery checklist

Render the figure and look at the PNG. Then check:
1. Nothing overlaps: text on lines, labels on borders, arrowheads under
   blocks.
2. Every colour maps to a concept, and the same concept has the same colour.
3. The figure uses four hues or fewer, plus gray.
4. Arrows start and end on borders and point in the flow direction.
5. Blocks in the same role have the same size, and stacks are centred.
6. Text is serif, symbols are italic, and no label is wider than its box.
7. It still reads in greyscale: tints and line styles distinguish things,
   not hue alone.
