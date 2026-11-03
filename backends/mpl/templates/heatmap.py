"""Heat map (attention weights / confusion matrix): sequential white->blue map,
thin white cell separators, token labels on both axes, values in cells."""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
import numpy as np
import mlfig

src = ["the", "cat", "sat", "on", "the", "mat"]
tgt = ["le", "chat", "s'est", "assis"]
rng = np.random.default_rng(1)
A = rng.random((len(tgt), len(src))) ** 4
A[np.arange(4), [0, 1, 2, 3]] += 2
A /= A.sum(1, keepdims=True)

fig, ax = mlfig.subplots(figsize=(3.6, 2.6))
im = ax.imshow(A, cmap="mlfig_seq", vmin=0, vmax=1)
ax.set_xticks(range(len(src)), src)
ax.set_yticks(range(len(tgt)), tgt)
ax.xaxis.tick_top()
for side in ax.spines.values():
    side.set_visible(False)
ax.set_xticks(np.arange(-.5, len(src)), minor=True)
ax.set_yticks(np.arange(-.5, len(tgt)), minor=True)
ax.grid(which="minor", color="white", lw=1.2)
ax.tick_params(which="minor", length=0)
for (i, j), v in np.ndenumerate(A):
    ax.text(j, i, f"{v:.2f}", ha="center", va="center", fontsize=6.5,
            color="white" if v > .55 else mlfig.C["ink"])
cb = fig.colorbar(im, ax=ax, shrink=.8, pad=.02)
cb.outline.set_visible(False)
cb.ax.tick_params(length=0)

mlfig.save(fig, Path(__file__).with_suffix(""))
