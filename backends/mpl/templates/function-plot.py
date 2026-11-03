"""Function plot: a curve, its derivative (grey, dashed), axes through the
origin, and the formula set beside the plot in the curve's colour."""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
import numpy as np
import mlfig

fig, (ax, side) = mlfig.subplots(1, 2, figsize=(4.8, 2.2), width_ratios=[2.6, 1])
z = np.linspace(-6, 6, 400)
s = 1 / (1 + np.exp(-z))

ax.plot(z, s, color=mlfig.C["blue2"], label="Sigmoid")
ax.plot(z, s * (1 - s), color=mlfig.C["gray"], lw=1.6, ls=(0, (4, 2)), label="Derivative")
ax.set(xlim=(-6, 6), ylim=(0, 1.05), xticks=[-6, 6], yticks=[0.5, 1])
mlfig.origin_axes(ax, xlabel="$z$")
ax.legend(loc="upper left")

# Formula panel: title and equation in the curve's hue.
side.axis("off")
side.text(0, .68, "Sigmoid", color=mlfig.C["blue2"], fontweight="bold", fontsize=11)
side.text(0, .40, r"$\sigma(z)=\dfrac{1}{1+e^{-z}}$", color=mlfig.C["blue2"], fontsize=12)

mlfig.save(fig, Path(__file__).with_suffix(""))
