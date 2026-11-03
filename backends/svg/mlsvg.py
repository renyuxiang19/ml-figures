"""mlsvg - tiny, dependency-free helper that writes SVG figures in the mlfig style.

Coordinates are SVG pixels, y pointing down. Every drawing call returns a Box
(or the item) so later calls can attach to its anchors:

    from mlsvg import Figure
    f = Figure()
    a = f.block(100, 300, "Multi-Head\\nAttention", "attention")
    n = f.block(100, a.n[1] - 4 - 8, "Add & Norm", "norm", h=16)
    f.arrow([a.n, n.s])
    f.save("out.svg")

Text supports light markup: "W^{Q}", "h_{t-1}", "$x$" (italic). Use "\\n" for
line breaks. The <style> and arrow markers are embedded on save, so the file
is self-contained and renders anywhere.
"""
from __future__ import annotations

import html
import re
from dataclasses import dataclass
from pathlib import Path

HERE = Path(__file__).resolve().parent
CSS = (HERE / "mlfig.css").read_text(encoding="utf-8")
DEFS = (HERE / "defs.svg").read_text(encoding="utf-8").strip()

FONT = 12.0        # px, matches .text in mlfig.css
SMALL = 10.0
LINE = 1.18        # line height in em
BLOCK_W, BLOCK_H, THIN_H = 80, 32, 16
RADIUS = 2.4


@dataclass
class Box:
    x: float
    y: float
    w: float
    h: float

    @property
    def c(self): return (self.x + self.w / 2, self.y + self.h / 2)
    @property
    def n(self): return (self.x + self.w / 2, self.y)
    @property
    def s(self): return (self.x + self.w / 2, self.y + self.h)
    @property
    def e(self): return (self.x + self.w, self.y + self.h / 2)
    @property
    def w_(self): return (self.x, self.y + self.h / 2)   # west ("w" is width)
    @property
    def nw(self): return (self.x, self.y)
    @property
    def ne(self): return (self.x + self.w, self.y)
    @property
    def sw(self): return (self.x, self.y + self.h)
    @property
    def se(self): return (self.x + self.w, self.y + self.h)

    def at(self, fx: float, fy: float):
        """Point at fractions (0..1) of the box, e.g. at(.25, 0) = a quarter along the top."""
        return (self.x + fx * self.w, self.y + fy * self.h)


def union(*boxes: Box, pad: float = 0, pad_top: float | None = None) -> Box:
    x0 = min(b.x for b in boxes) - pad
    y0 = min(b.y for b in boxes) - (pad if pad_top is None else pad_top)
    x1 = max(b.x + b.w for b in boxes) + pad
    y1 = max(b.y + b.h for b in boxes) + pad
    return Box(x0, y0, x1 - x0, y1 - y0)


_MARK = re.compile(r"\^\{([^}]*)\}|_\{([^}]*)\}|\^(\w)|_(\w)|\$([^$]*)\$")


def _rich(s: str) -> tuple[str, float]:
    """Markup -> tspans; returns (svg, approx width in em)."""
    out, width, pos = [], 0.0, 0
    for m in _MARK.finditer(s):
        plain = s[pos:m.start()]
        out.append(html.escape(plain)); width += 0.5 * len(plain)
        sup, sub, sup1, sub1, ital = m.groups()
        if sup is not None or sup1 is not None:
            t = sup if sup is not None else sup1
            out.append(f'<tspan baseline-shift="super" font-size="70%">{html.escape(t)}</tspan>')
            width += 0.36 * len(t)
        elif sub is not None or sub1 is not None:
            t = sub if sub is not None else sub1
            out.append(f'<tspan baseline-shift="sub" font-size="70%">{html.escape(t)}</tspan>')
            width += 0.36 * len(t)
        else:
            out.append(f'<tspan font-style="italic">{html.escape(ital)}</tspan>')
            width += 0.5 * len(ital)
        pos = m.end()
    tail = s[pos:]
    out.append(html.escape(tail)); width += 0.5 * len(tail)
    return "".join(out), width


class Figure:
    def __init__(self, pad: float = 6):
        self.pad = pad
        self.back: list[str] = []    # regions, drawn first
        self.items: list[str] = []
        self.bounds = [float("inf"), float("inf"), float("-inf"), float("-inf")]

    # ---------------------------------------------------------- bookkeeping
    def _grow(self, x0, y0, x1, y1):
        b = self.bounds
        b[0], b[1], b[2], b[3] = min(b[0], x0), min(b[1], y0), max(b[2], x1), max(b[3], y1)

    def raw(self, svg: str, bbox: Box | None = None, back: bool = False):
        """Insert hand-written SVG. Pass its bbox so the canvas grows to fit."""
        (self.back if back else self.items).append(svg)
        if bbox:
            self._grow(bbox.x, bbox.y, bbox.x + bbox.w, bbox.y + bbox.h)

    # ------------------------------------------------------------- text
    def text(self, x, y, s: str, cls: str = "", anchor: str = "middle", size: float | None = None):
        style = f' style="font-size:{size:g}px"' if size else ""
        size = size or (SMALL if "small" in cls.split() else FONT)
        lines = s.split("\n")
        y0 = y - (len(lines) - 1) * LINE * size / 2
        spans, widest = [], 0.0
        for i, ln in enumerate(lines):
            body, w = _rich(ln)
            widest = max(widest, w)
            spans.append(f'<tspan x="{x:g}" y="{y0 + i * LINE * size:g}">{body}</tspan>')
        a = {"middle": "", "start": " start", "end": " end"}[anchor]
        self.items.append(f'<text class="{(cls + a).strip()}"{style}>{"".join(spans)}</text>')
        wpx = widest * size
        x0 = {"middle": x - wpx / 2, "start": x, "end": x - wpx}[anchor]
        h = len(lines) * LINE * size
        self._grow(x0, y0 - size * .6, x0 + wpx, y0 - size * .6 + h)
        return Box(x0, y0 - size * .6, wpx, h)

    # ----------------------------------------------------------- shapes
    def block(self, cx, cy, label: str = "", role: str = "gray", w=BLOCK_W, h=BLOCK_H,
              cls: str = "", text_cls: str = "") -> Box:
        """Rounded operator block, centred at (cx, cy). role = semantic or palette name."""
        b = Box(cx - w / 2, cy - h / 2, w, h)
        classes = " ".join(filter(None, ["blk", f"f-{role}", cls]))
        self.items.append(f'<rect class="{classes}" x="{b.x:g}" y="{b.y:g}" '
                          f'width="{w:g}" height="{h:g}" rx="{RADIUS}"/>')
        self._grow(b.x, b.y, b.x + w, b.y + h)
        if label:
            self.text(cx, cy, label, text_cls)
        return b

    def thin(self, cx, cy, label, role, w=BLOCK_W) -> Box:
        return self.block(cx, cy, label, role, w=w, h=THIN_H)

    def above(self, box: Box, gap: float, label="", role="gray", w=BLOCK_W, h=BLOCK_H) -> Box:
        """New block centred over `box`, its bottom `gap` px above box's top."""
        return self.block(box.n[0], box.y - gap - h / 2, label, role, w=w, h=h)

    def circle(self, cx, cy, r, cls="line", label="") -> Box:
        self.items.append(f'<circle class="{cls}" cx="{cx:g}" cy="{cy:g}" r="{r:g}"/>')
        self._grow(cx - r, cy - r, cx + r, cy + r)
        if label:
            self.text(cx, cy, label)
        return Box(cx - r, cy - r, 2 * r, 2 * r)

    def sum(self, cx, cy, sym="+", r=6) -> Box:
        b = self.circle(cx, cy, r, "line")
        self.text(cx, cy + .5, sym, "small")
        return b

    def neuron(self, cx, cy, role="hidden", r=14, label="") -> Box:
        self.items.append(f'<circle class="neuron fn-{role} s-{role}" cx="{cx:g}" cy="{cy:g}" r="{r:g}"/>')
        self._grow(cx - r, cy - r, cx + r, cy + r)
        if label:
            self.text(cx, cy, label, f"t-{role}")
        return Box(cx - r, cy - r, 2 * r, 2 * r)

    def tensor(self, x, y, cols, rows, role="x", cell=9.5, grid_role: str | None = None,
               hot: list[tuple[int, int]] = ()) -> Box:
        """Gridded matrix with top-left at (x, y); `hot` cells get the emphasis tint."""
        w, h = cols * cell, rows * cell
        g = f' kl-{grid_role}' if grid_role else ''
        parts = [f'<rect class="cell f-{role}" x="{x:g}" y="{y:g}" width="{w:g}" height="{h:g}"/>']
        parts += [f'<rect class="fe-{role}" x="{x + c * cell:g}" y="{y + r * cell:g}" '
                  f'width="{cell:g}" height="{cell:g}"/>' for r, c in hot]
        d = "".join(f"M{x + i * cell:g},{y:g}v{h:g}" for i in range(1, cols)) + \
            "".join(f"M{x:g},{y + j * cell:g}h{w:g}" for j in range(1, rows))
        parts.append(f'<path class="grid{g}" d="{d}"/>')
        parts.append(f'<rect class="cell{g}" fill="none" x="{x:g}" y="{y:g}" width="{w:g}" height="{h:g}"/>')
        self.items.append("".join(parts))
        self._grow(x, y, x + w, y + h)
        return Box(x, y, w, h)

    # ------------------------------------------------------------ lines
    def path(self, pts, cls="line", arrow=True, back=False):
        d = "M" + " L".join(f"{x:g},{y:g}" for x, y in pts)
        a = " arrow" if arrow and "edge" not in cls else (" arrow-navy" if arrow else "")
        (self.back if back else self.items).append(f'<path class="{cls}{a}" d="{d}"/>')
        for x, y in pts:
            self._grow(x, y, x, y)

    def arrow(self, pts, cls="line"):
        self.path(pts, cls, True)

    def connect(self, p, q, cls="line", arrow=True, via: str = "straight", off: float = 0):
        """Join two points. via='hv' goes horizontal then vertical, 'vh' the reverse,
        'side' leaves p horizontally by `off`, runs vertically, enters q horizontally."""
        if via == "hv":
            pts = [p, (q[0], p[1]), q]
        elif via == "vh":
            pts = [p, (p[0], q[1]), q]
        elif via == "side":
            pts = [p, (p[0] + off, p[1]), (p[0] + off, q[1]), q]
        else:
            pts = [p, q]
        self.path(pts, cls, arrow)

    def edge(self, p, q, halo=True):
        """Network connection: thick navy line with a white halo for crossings."""
        if halo:
            self.items.append(f'<path class="halo" d="M{p[0]:g},{p[1]:g} L{q[0]:g},{q[1]:g}"/>')
        self.items.append(f'<path class="edge" d="M{p[0]:g},{p[1]:g} L{q[0]:g},{q[1]:g}"/>')

    # ---------------------------------------------------------- groups
    def region(self, box: Box, role: str, title: str = "", corner: str = "nw") -> Box:
        """Tinted, dotted background area. Drawn behind everything."""
        self.back.append(f'<rect class="region fr-{role}" x="{box.x:g}" y="{box.y:g}" '
                         f'width="{box.w:g}" height="{box.h:g}"/>')
        self._grow(box.x, box.y, box.x + box.w, box.y + box.h)
        if title:
            if corner == "nw":
                self.text(box.x + 7, box.y + 10, title, "title", anchor="start")
            elif corner == "ne":
                self.text(box.x + box.w - 7, box.y + 10, title, "title", anchor="end")
            else:
                self.text(box.c[0], box.y + box.h - 10, title, "title")
        return box

    def group(self, box: Box, cls: str = "group") -> Box:
        """Dashed outline for a repeated or logical sub-structure."""
        self.items.append(f'<rect class="{cls}" x="{box.x:g}" y="{box.y:g}" '
                          f'width="{box.w:g}" height="{box.h:g}" rx="{RADIUS}"/>')
        self._grow(box.x, box.y, box.x + box.w, box.y + box.h)
        return box

    # ------------------------------------------------------------- save
    def svg(self, title: str = "") -> str:
        x0, y0, x1, y1 = self.bounds
        p = self.pad
        x0, y0, w, h = x0 - p, y0 - p, x1 - x0 + 2 * p, y1 - y0 + 2 * p
        t = f"<title>{html.escape(title)}</title>\n" if title else ""
        return (f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="{x0:g} {y0:g} {w:g} {h:g}" '
                f'width="{w:g}" height="{h:g}">\n{t}<!-- mlfig:begin -->\n<style><![CDATA[\n{CSS}]]></style>\n'
                f'{DEFS}\n<!-- mlfig:end -->\n'
                f'<rect x="{x0:g}" y="{y0:g}" width="{w:g}" height="{h:g}" fill="#FFFFFF"/>\n'
                + "\n".join(self.back + self.items) + "\n</svg>\n")

    def save(self, path, title: str = ""):
        Path(path).write_text(self.svg(title), encoding="utf-8")
        return path
