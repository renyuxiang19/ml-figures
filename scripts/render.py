#!/usr/bin/env python3
"""Render a figure source to viewable outputs and run basic sanity checks.

    python scripts/render.py figure.svg          # -> figure.png (+ checks)
    python scripts/render.py figure.tex          # -> figure.pdf, figure.png
    python scripts/render.py figure.tex --svg    #    ... and figure.svg (dvisvgm)
    python scripts/render.py figure.py           # runs the plotting script

The PNG exists so the figure can be *looked at* before it is handed over:
open it and inspect it. Checks print as WARN lines; fix them, re-render.

Converters are discovered at run time; whichever exists is used:
  SVG -> PNG : rsvg-convert, cairosvg (pip), inkscape, Chrome/Edge headless, ImageMagick
  TeX -> PDF : latexmk or pdflatex (mlfig.sty is put on TEXINPUTS automatically)
  PDF -> PNG : pdftoppm, ImageMagick, inkscape
"""
from __future__ import annotations

import argparse
import os
import re
import shutil
import subprocess
import sys
import tempfile
import xml.etree.ElementTree as ET
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SVG_NS = "{http://www.w3.org/2000/svg}"


def run(cmd, **kw) -> subprocess.CompletedProcess:
    return subprocess.run(cmd, capture_output=True, text=True, errors="replace", **kw)


def which(*names) -> str | None:
    for n in names:
        p = shutil.which(n)
        if p:
            return p
    return None


def browser() -> str | None:
    found = which("chromium", "chromium-browser", "google-chrome", "chrome", "msedge")
    if found:
        return found
    for p in [r"C:\Program Files\Google\Chrome\Application\chrome.exe",
              r"C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe",
              r"C:\Program Files\Microsoft\Edge\Application\msedge.exe",
              "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome",
              "/Applications/Microsoft Edge.app/Contents/MacOS/Microsoft Edge"]:
        if Path(p).exists():
            return p
    return None


def warn(msg: str) -> None:
    print(f"WARN  {msg}")


# ------------------------------------------------------------------- SVG
def _num(v: str | None) -> float | None:
    if v is None:
        return None
    m = re.match(r"\s*(-?[\d.]+)", v)
    return float(m.group(1)) if m else None


def check_svg(path: Path) -> tuple[float, float]:
    try:
        tree = ET.parse(path)
    except ET.ParseError as e:
        sys.exit(f"ERROR invalid XML: {e}")
    root = tree.getroot()
    vb = root.get("viewBox")
    if not vb:
        warn("root <svg> has no viewBox; it will not scale cleanly")
        w, h = _num(root.get("width")) or 800, _num(root.get("height")) or 600
        x0 = y0 = 0
    else:
        x0, y0, w, h = (float(v) for v in vb.replace(",", " ").split())
    css = "".join(s.text or "" for s in root.iter(f"{SVG_NS}style"))
    if not css:
        warn("no <style> block: copy the mlfig:begin..end block from a template")
    defined = set(re.findall(r"\.([A-Za-z][\w-]*)", css))
    ids = {e.get("id") for e in root.iter() if e.get("id")}
    unknown = set()
    for e in root.iter():
        for c in (e.get("class") or "").split():
            if c not in defined:
                unknown.add(c)
        for attr in ("marker-end", "marker-start", "fill", "stroke", "clip-path"):
            m = re.match(r"url\(#([^)]+)\)", e.get(attr) or "")
            if m and m.group(1) not in ids:
                warn(f"<{e.tag.replace(SVG_NS, '')}> references undefined #{m.group(1)}")
    if unknown:
        warn("classes not in mlfig.css (typo?): " + ", ".join(sorted(unknown)))
    # Text anchored outside the canvas is almost always a layout slip.
    for t in root.iter(f"{SVG_NS}text"):
        x, y = _num(t.get("x")), _num(t.get("y"))
        if t.get("transform") or x is None or y is None:
            continue
        if not (x0 - 1 <= x <= x0 + w + 1 and y0 - 1 <= y <= y0 + h + 1):
            label = "".join(t.itertext()).strip()[:30]
            warn(f"text '{label}' at ({x:g},{y:g}) lies outside the viewBox")
    return w, h


def svg_to_png(src: Path, dst: Path, w: float, h: float, scale: float) -> str:
    W, H = int(round(w * scale)), int(round(h * scale))
    if (exe := which("rsvg-convert")):
        r = run([exe, "-z", str(scale), "-b", "white", "-o", str(dst), str(src)])
        if r.returncode == 0:
            return "rsvg-convert"
    try:
        import cairosvg  # type: ignore
        cairosvg.svg2png(url=str(src), write_to=str(dst), scale=scale, background_color="white")
        return "cairosvg"
    except Exception:
        pass
    if (exe := which("inkscape")):
        r = run([exe, str(src), "--export-type=png", f"--export-filename={dst}",
                 f"--export-width={W}", "--export-background=white"])
        if r.returncode == 0:
            return "inkscape"
    if (exe := browser()):
        with tempfile.TemporaryDirectory() as tmp:
            html = Path(tmp) / "page.html"
            html.write_text(
                "<!doctype html><html><body style='margin:0;background:#fff'>"
                f"<img src='{src.resolve().as_uri()}' style='display:block;width:{w}px;height:{h}px'>"
                "</body></html>", encoding="utf-8")
            r = run([exe, "--headless=new", "--disable-gpu", "--hide-scrollbars",
                     f"--user-data-dir={tmp}", f"--force-device-scale-factor={scale}",
                     f"--window-size={int(w)},{int(h)}", f"--screenshot={dst}",
                     "--allow-file-access-from-files", html.as_uri()], timeout=60)
            if dst.exists():
                return "headless browser"
    if (exe := which("magick")):
        r = run([exe, "-density", str(int(96 * scale)), "-background", "white", str(src), str(dst)])
        if r.returncode == 0:
            warn("rendered with ImageMagick; its SVG support is approximate - "
                 "markers and CSS may be off in the PNG even if the SVG is fine")
            return "ImageMagick"
    sys.exit("ERROR no SVG rasteriser found (install one: pip install cairosvg, "
             "or rsvg-convert / inkscape / Chrome)")


# ------------------------------------------------------------------- TeX
def tex_to_pdf(src: Path, outdir: Path) -> Path:
    env = dict(os.environ)
    sep = ";" if os.name == "nt" else ":"
    env["TEXINPUTS"] = f".{sep}{ROOT / 'backends' / 'tikz'}{sep}{env.get('TEXINPUTS', '')}"
    if (exe := which("latexmk")):
        cmd = [exe, "-pdf", "-interaction=nonstopmode", "-halt-on-error",
               f"-outdir={outdir}", src.name]
    elif (exe := which("pdflatex")):
        cmd = [exe, "-interaction=nonstopmode", "-halt-on-error",
               f"-output-directory={outdir}", src.name]
    else:
        sys.exit("ERROR no LaTeX found (install TeX Live / MiKTeX), or use the SVG backend")
    r = run(cmd, cwd=src.parent, env=env, timeout=300)
    log = outdir / (src.stem + ".log")
    text = log.read_text(errors="replace") if log.exists() else r.stdout
    if r.returncode != 0:
        errs = re.findall(r"^! .*(?:\n.*){0,3}", text, re.M)
        sys.exit("ERROR LaTeX failed:\n" + ("\n".join(errs[:3]) or r.stdout[-2000:]))
    for m in re.findall(r"Missing character: There is no .*", text):
        warn(m)
    if re.search(r"Overfull \\hbox", text):
        warn("overfull hbox - some text is wider than its node; add \\\\ or widen the node")
    return outdir / (src.stem + ".pdf")


def pdf_to_png(pdf: Path, dst: Path, dpi: int) -> None:
    if (exe := which("pdftoppm")):
        run([exe, "-png", "-r", str(dpi), "-singlefile", str(pdf), str(dst.with_suffix(""))])
    elif (exe := which("magick")):
        run([exe, "-density", str(dpi), str(pdf), "-background", "white", "-flatten", str(dst)])
    elif (exe := which("inkscape")):
        run([exe, str(pdf), "--export-type=png", f"--export-filename={dst}", f"--export-dpi={dpi}"])
    else:
        warn("no PDF rasteriser (pdftoppm / ImageMagick / inkscape); PNG skipped")


# ------------------------------------------------------------------- main
def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("source", type=Path)
    ap.add_argument("--scale", type=float, default=2.0, help="SVG raster scale (default 2)")
    ap.add_argument("--dpi", type=int, default=300, help="PDF raster dpi (default 300)")
    ap.add_argument("--svg", action="store_true", help="TeX only: also export SVG via dvisvgm")
    a = ap.parse_args()
    src = a.source.resolve()
    if not src.exists():
        sys.exit(f"ERROR not found: {src}")
    ext = src.suffix.lower()

    if ext == ".svg":
        w, h = check_svg(src)
        png = src.with_suffix(".png")
        how = svg_to_png(src, png, w, h, a.scale)
        print(f"OK    {png}  ({how})")
    elif ext == ".tex":
        pdf = tex_to_pdf(src, src.parent)
        for junk in (".aux", ".log", ".fls", ".fdb_latexmk"):
            src.with_suffix(junk).unlink(missing_ok=True)
        print(f"OK    {pdf}")
        pdf_to_png(pdf, src.with_suffix(".png"), a.dpi)
        if src.with_suffix(".png").exists():
            print(f"OK    {src.with_suffix('.png')}")
        if a.svg and (exe := which("dvisvgm")):
            run([exe, "--pdf", "--no-fonts", "-o", str(src.with_suffix(".svg")), str(pdf)])
            print(f"OK    {src.with_suffix('.svg')}")
    elif ext == ".py":
        env = dict(os.environ)
        env["PYTHONPATH"] = f"{ROOT / 'backends' / 'mpl'}{os.pathsep}{env.get('PYTHONPATH', '')}"
        env.setdefault("MPLBACKEND", "Agg")
        r = run([sys.executable, str(src)], cwd=src.parent, env=env, timeout=300)
        sys.stdout.write(r.stdout)
        for line in r.stderr.splitlines():
            if "findfont" in line:
                warn("a requested font is missing; matplotlib fell back to another serif")
                break
        if r.returncode != 0:
            sys.exit("ERROR script failed:\n" + r.stderr[-2000:])
        print("OK    script finished")
    else:
        sys.exit("ERROR expected .svg, .tex or .py")
    return 0


if __name__ == "__main__":
    sys.exit(main())
