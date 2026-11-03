"""mlfig - matplotlib side of the mlfig style.

    import mlfig
    mlfig.use()                       # apply mlfig.mplstyle + register colormaps
    fig, ax = mlfig.subplots()
    ax.plot(x, y, color=mlfig.C["blue2"])
    mlfig.origin_axes(ax)             # axes through (0, 0), as in textbook plots
    mlfig.save(fig, "relu")           # relu.pdf + relu.svg + relu.png

Colours: C[name] is the base hue for any palette or semantic name
("blue", "attention", "query", ...). tint(name, "block"|"node"|"region"|"emphasis")
and shade(name, "outline"|"label") give the same tints the diagrams use, so a
plot placed next to a diagram shares its colours.
"""
from __future__ import annotations

import json
from pathlib import Path

import matplotlib as mpl
import matplotlib.pyplot as plt
from matplotlib.colors import LinearSegmentedColormap

HERE = Path(__file__).resolve().parent
_T = json.loads((HERE / "mlfig_tokens.json").read_text(encoding="utf-8"))

C: dict[str, str] = dict(_T["palette"])
C.update({k: _T["palette"][v] for k, v in _T["semantic"].items()})
_FILLS = _T["fills"]


def tint(name: str, level: str = "block") -> str:
    return _FILLS[name][level]


def shade(name: str, level: str = "label") -> str:
    return _FILLS[name][level]


def _register_cmaps() -> None:
    maps = {
        # white -> blue -> navy: attention maps, confusion matrices, densities
        "mlfig_seq": [C["paper"], tint("blue", "node"), C["blue"], C["navy"]],
        # red <- white -> blue: signed quantities (weights, gradients, differences)
        "mlfig_div": [C["red"], tint("red", "node"), C["paper"], tint("blue", "node"), C["blue"]],
    }
    for name, cols in maps.items():
        if name not in mpl.colormaps:
            mpl.colormaps.register(LinearSegmentedColormap.from_list(name, cols))
            mpl.colormaps.register(LinearSegmentedColormap.from_list(name + "_r", cols[::-1]))


_FONT_FILES = ["lmroman10-regular.otf", "lmroman10-bold.otf",
               "lmroman10-italic.otf", "lmroman10-bolditalic.otf"]


def _register_fonts() -> None:
    """Latin Modern ships with every TeX distribution but matplotlib does not
    look there. Register it if found; otherwise the serif fallback list applies."""
    import shutil
    import subprocess
    from matplotlib import font_manager as fm
    if any(f.name == "Latin Modern Roman" for f in fm.fontManager.ttflist):
        return
    paths = []
    if shutil.which("kpsewhich"):
        try:
            r = subprocess.run(["kpsewhich", *_FONT_FILES], capture_output=True, text=True, timeout=10)
            paths = [p for p in r.stdout.split("\n") if p.strip()]
        except Exception:
            paths = []
    for p in paths:
        try:
            fm.fontManager.addfont(p.strip())
        except Exception:
            pass


def use() -> None:
    """Apply the style. Safe to call more than once."""
    _register_cmaps()
    _register_fonts()
    plt.style.use(str(HERE / "mlfig.mplstyle"))


def subplots(*args, **kw):
    use()
    kw.setdefault("layout", "constrained")
    return plt.subplots(*args, **kw)


def origin_axes(ax, arrows: bool = False, xlabel: str | None = None, ylabel: str | None = None) -> None:
    """Draw the x/y axes through the origin with no frame, like a textbook
    function plot. Labels go at the positive ends of the axes."""
    for side in ("top", "right"):
        ax.spines[side].set_visible(False)
    ax.spines["left"].set_position("zero")
    ax.spines["bottom"].set_position("zero")
    if arrows:
        ax.plot(1, 0, ">k", transform=ax.get_yaxis_transform(), clip_on=False, ms=4)
        ax.plot(0, 1, "^k", transform=ax.get_xaxis_transform(), clip_on=False, ms=4)
    if xlabel:   # above the axis, so it never collides with the last tick label
        ax.annotate(xlabel, xy=(1, 0), xycoords=("axes fraction", "data"),
                    xytext=(0, 4), textcoords="offset points", ha="right", va="bottom")
    if ylabel:
        ax.annotate(ylabel, xy=(0, 1), xycoords=("data", "axes fraction"),
                    xytext=(-4, 0), textcoords="offset points", ha="right", va="top")


def label_curve(ax, x, y, text: str, color: str, dx: float = 4, dy: float = 4, **kw) -> None:
    """Direct label next to a curve point - preferred over a legend for <= 4 lines."""
    ax.annotate(text, (x, y), xytext=(dx, dy), textcoords="offset points",
                color=color, **kw)


def end_labels(ax, x, ys, texts, colors, min_gap: float = 9, dx: float = 4) -> None:
    """Label several lines at their right end, nudging labels apart vertically
    so they never overlap (min_gap in points). Call after the axis limits are
    final, because the spacing is computed in screen space."""
    pts_per_px = 72 / ax.figure.dpi
    y_px = [ax.transData.transform((x, y))[1] for y in ys]
    last = None
    for i in sorted(range(len(ys)), key=lambda i: y_px[i]):
        target = y_px[i] if last is None else max(y_px[i], last + min_gap / pts_per_px)
        last = target
        ax.annotate(texts[i], (x, ys[i]), xytext=(dx, (target - y_px[i]) * pts_per_px),
                    textcoords="offset points", color=colors[i], va="center", ha="left",
                    annotation_clip=False)


def save(fig, stem: str | Path, formats=("pdf", "svg", "png")) -> list[Path]:
    """Save next to each other in several formats; returns the paths."""
    stem = Path(stem)
    out = []
    for ext in formats:
        p = stem.with_suffix("." + ext)
        fig.savefig(p)
        out.append(p)
    return out
