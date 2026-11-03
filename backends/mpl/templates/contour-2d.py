"""2-D parameter-space plot: grey dashed loss contours, a coloured constraint
(L2 ball), axes through the origin and bold coloured annotations - the
classic regularisation / optimisation-trajectory picture."""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
import numpy as np
import mlfig

fig, ax = mlfig.subplots(figsize=(3.6, 3.2))
w1, w2 = np.meshgrid(np.linspace(-1.5, 4.5, 300), np.linspace(-1.5, 4.5, 300))
c, th = np.array([2.6, 2.2]), np.deg2rad(-15)
u = (w1 - c[0]) * np.cos(th) - (w2 - c[1]) * np.sin(th)
v = (w1 - c[0]) * np.sin(th) + (w2 - c[1]) * np.cos(th)
loss = (u / 1.5) ** 2 + (v / .7) ** 2

ax.contour(w1, w2, loss, levels=[.4, 1.6, 3.6], colors=mlfig.C["gray"],
           linestyles=[(0, (4, 2))], linewidths=1.6)
for r in (.5, 1.0, 1.5):
    ax.add_patch(mlfig.plt.Circle((0, 0), r, fill=False, color=mlfig.C["red"], lw=1.6))

opt, reg = c, np.array([1.0, 1.12])
ax.plot(*opt, "o", color="k", ms=4)
ax.plot(*reg, "o", color="k", ms=4)
# Annotation text lives in empty space; arrows point at the dots.
ax.annotate("Minimum", opt, xytext=(2.3, 4.0), fontweight="bold",
            arrowprops=dict(arrowstyle="-|>", lw=.8, color="k", shrinkB=4))
ax.annotate("Regularised minimum", reg, xytext=(-1.3, 3.2), fontweight="bold",
            arrowprops=dict(arrowstyle="-|>", lw=.8, color="k", shrinkB=4))
ax.text(0, -1.75, "L2 penalty", color=mlfig.C["red"], fontweight="bold", ha="center")

ax.set(xlim=(-1.8, 4.5), ylim=(-2, 4.5), xticks=[], yticks=[], aspect="equal")
mlfig.origin_axes(ax, arrows=True, xlabel="$w_1$", ylabel="$w_2$")

mlfig.save(fig, Path(__file__).with_suffix(""))
