"""Banner subtitle copy/size and a compact toolkit. Run: python -m pytest -q"""
import pathlib
import re
import sys
import xml.etree.ElementTree as ET

ROOT = pathlib.Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "scripts"))
import banner  # noqa: E402
import panels  # noqa: E402

NS = "{http://www.w3.org/2000/svg}"


def subtitle(svg):
    root = ET.fromstring(svg)
    for t in root.iter(NS + "text"):
        txt = "".join(t.itertext())
        if "harnesses" in txt or "harness engineering" in txt:
            return t, txt
    raise AssertionError("subtitle not found")


def test_banner_subtitle_is_short_and_readable():
    for svg in (banner.banner(), (ROOT / "assets" / "banner.svg").read_text()):
        el, txt = subtitle(svg)
        assert re.sub(r"\s+", " ", txt).strip() == "agents · harnesses · inference"
        assert float(el.get("font-size")) >= 22
        assert el.get("fill").lower() not in ("#8b949e", "#6e7681"), "should be brighter than the old grey"


def tiles(svg):
    root = ET.fromstring(svg)
    out = []
    for g in root.iter(NS + "g"):
        if "pop" in (g.get("class") or ""):
            r = g.find(NS + "rect")
            out.append((float(r.get("x")), float(r.get("y")), float(r.get("width"))))
    return out


def test_toolkit_tiles_and_icons_are_compact():
    svg = panels.tools()
    t = tiles(svg)
    assert len(t) == 40
    assert all(w <= 54 for _, _, w in t)
    for size in re.findall(r'<svg x="[\d.]+" y="[\d.]+" width="(\d+)"', svg):
        assert int(size) <= 26
    for scale in re.findall(r"scale\(([\d.]+)\)", svg.split("</style>", 1)[1]):
        assert float(scale) <= 1.1


def test_toolkit_labels_have_room():
    t = tiles(panels.tools())
    row = [x for x, y, _ in t if y == t[0][1]]
    assert min(b - a for a, b in zip(row, row[1:])) >= 70


def test_toolkit_is_shorter_than_before():
    h = int(re.search(r'height="(\d+)"', panels.tools()).group(1))
    assert h <= 600
