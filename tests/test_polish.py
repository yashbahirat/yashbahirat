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


def test_banner_has_no_subtitle_line():
    # "agents · harnesses · inference" already rotates in the role strip right below the banner
    for svg in (banner.banner(), (ROOT / "assets" / "banner.svg").read_text()):
        for gone in ("harnesses", "harness engineering", "inference engineering"):
            assert gone not in svg, gone
        assert ">YASH<" in svg and ">BAHIRAT<" in svg


def test_banner_carries_the_role_and_is_centred():
    for svg in (banner.banner(), (ROOT / "assets" / "banner.svg").read_text()):
        text = re.sub(r"\s+", " ", re.sub(r"<[^>]+>", " ", svg.split("</style>", 1)[1]))
        assert "Junior Agentic Coder at Tradeify" in text
    svg = banner.banner()
    role = re.search(r'<text class="role" x="[\d.]+" y="([\d.]+)" font-size="([\d.]+)"', svg)
    assert role and float(role.group(2)) >= 24
    names = [float(y) for y in re.findall(r'<text x="78" y="([\d.]+)"[^>]*font-size="92"', svg)]
    top = min(names) - 92 * 0.72
    bottom = float(role.group(1)) + 6
    height = float(re.search(r'viewBox="0 0 \d+ (\d+)"', svg).group(1))
    assert abs((top + bottom) / 2 - height / 2) <= 12


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


def test_role_strip_is_merged_into_banner():
    readme = (ROOT / "README.md").read_text()
    assert "assets/hero." not in readme
    assert not list((ROOT / "assets").glob("hero*.svg"))
    assert '("hero", hero)' not in (ROOT / "scripts" / "panels.py").read_text()
    assert readme.index("assets/banner.svg") < readme.index("contributions-badge.svg")
