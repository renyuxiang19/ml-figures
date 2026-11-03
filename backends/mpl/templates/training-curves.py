"""Training curves: train (solid) vs validation (dashed) per method, one hue
per method, labels written at the line ends instead of a colour legend."""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
import numpy as np
import mlfig

rng = np.random.default_rng(0)
steps = np.arange(1, 101)
runs = {"SGD": ("blue2", 0.9), "Momentum": ("red", 0.6), "Adam": ("green", 0.4)}

fig, ax = mlfig.subplots(figsize=(4.2, 2.8))
ends, names, hues = [], [], []
for name, (hue, k) in runs.items():
    train = 2.3 * np.exp(-steps / (60 * k)) + 0.15 + 0.02 * rng.standard_normal(steps.size)
    val = train + 0.08 + 0.002 * steps * (1 - k)
    ax.plot(steps, train, color=mlfig.C[hue], lw=1.6)
    ax.plot(steps, val, color=mlfig.C[hue], lw=1.2, ls=(0, (4, 2)))
    ends.append(val[-1]); names.append(name); hues.append(mlfig.C[hue])

ax.set(xlabel="Epoch", ylabel="Loss", xlim=(0, 100), ylim=(0, 2.5))
mlfig.end_labels(ax, steps[-1], ends, names, hues)     # after limits are fixed

# Line style legend only (colour is already labelled directly).
ax.plot([], [], color="k", lw=1.6, label="train")
ax.plot([], [], color="k", lw=1.2, ls=(0, (4, 2)), label="validation")
ax.legend(loc="upper right", frameon=False)

mlfig.save(fig, Path(__file__).with_suffix(""))
