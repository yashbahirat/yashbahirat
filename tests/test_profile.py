"""Guards for the profile README and its generated SVGs.

Run: pytest -q   (from repo root)
"""
import colorsys
import datetime as dt
import hashlib
import pathlib
import re
import sys
import xml.etree.ElementTree as ET

import pytest

ROOT = pathlib.Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "scripts"))

import banner  # noqa: E402
import contrib_card  # noqa: E402
import panels  # noqa: E402

ACCENT = "#F0883E"
WINDOW_BUTTONS = {"#ff5f57", "#febc2e", "#28c840"}
HUE_TOLERANCE_DEG = 14
NEUTRAL_MAX_CHROMA = 0.10

TOOLKIT = ["Claude Code", "Anthropic API", "OpenAI", "MCP", "LangGraph", "Ollama",
           "Python", "PyTorch", "Streamlit", "FastAPI", "Docker", "Cloudflare"]

PANELS = {"hero": panels.hero, "quote": panels.quote, "agent": panels.agent,
          "projects": panels.projects, "toolkit": panels.tools}


# ───────────────────────── helpers ─────────────────────────
def mock_stats():
    return contrib_card.stats(contrib_card.mock_days())


def generated_svgs():
    s = mock_stats()
    out = {name: fn() for name, fn in PANELS.items()}
    out["banner"] = banner.banner()
    out["footer"] = banner.footer()
    for theme in ("dark", "light"):
        out[f"contributions-{theme}"] = contrib_card.svg(s, "yashbahirat", contrib_card.THEMES[theme])
    out["contributions-badge"] = contrib_card.badge_svg("contributions", f"{s['total']:,}")
    return out


SVGS = generated_svgs()
HEX = re.compile(r"#(?:[0-9a-fA-F]{6}|[0-9a-fA-F]{3})\b")


def norm(h):
    h = h.lower()
    if len(h) == 4:
        h = "#" + "".join(c * 2 for c in h[1:])
    return h


def hue_sat(h):
    r, g, b = (int(norm(h)[i:i + 2], 16) / 255 for i in (1, 3, 5))
    hh, ll, ss = colorsys.rgb_to_hls(r, g, b)
    return hh * 360, ss, ll


def chroma(h):
    rgb = [int(norm(h)[i:i + 2], 16) / 255 for i in (1, 3, 5)]
    return max(rgb) - min(rgb)


def is_on_palette(h):
    """Neutral grey (GitHub's greys are slightly blue-tinted, so judge by chroma), or the accent hue."""
    h = norm(h)
    if h in WINDOW_BUTTONS:
        return True
    if chroma(h) <= NEUTRAL_MAX_CHROMA:
        return True
    hue, _, _ = hue_sat(h)
    acc_hue = hue_sat(ACCENT)[0]
    return min(abs(hue - acc_hue), 360 - abs(hue - acc_hue)) <= HUE_TOLERANCE_DEG


def colours_outside_logos(svg_text):
    """Every hex colour in the SVG except inside elements marked class="logo" (brand marks)."""
    root = ET.fromstring(svg_text)
    found = []

    def walk(el):
        if "logo" in (el.get("class") or "").split():
            return
        for attr in ("fill", "stroke", "stop-color", "color", "style"):
            found.extend(HEX.findall(el.get(attr) or ""))
        if el.tag.endswith("style") and el.text:
            css = re.sub(r"url\(data:[^)]*\)", "", el.text)  # skip embedded fonts
            found.extend(HEX.findall(css))
        for child in el:
            walk(child)

    walk(root)
    return found


# ───────────────────────── SVG validity ─────────────────────────
@pytest.mark.parametrize("name", sorted(SVGS))
def test_generated_svg_is_valid_standalone_xml(name):
    ET.fromstring(SVGS[name])


@pytest.mark.parametrize("path", sorted((ROOT / "assets").glob("*.svg")), ids=lambda p: p.name)
def test_committed_svg_is_valid_standalone_xml(path):
    ET.fromstring(path.read_text())


# ───────────────────────── no gradients, one accent ─────────────────────────
@pytest.mark.parametrize("name", sorted(SVGS))
def test_no_gradients_or_glows(name):
    svg = SVGS[name]
    assert "Gradient" not in svg, "gradient definition found"
    assert "feGaussianBlur" not in svg, "glow/blur filter found"


@pytest.mark.parametrize("name", sorted(SVGS))
def test_single_accent_colour(name):
    off = sorted({norm(c) for c in colours_outside_logos(SVGS[name]) if not is_on_palette(c)})
    assert not off, f"off-palette colours: {off}"


def test_accent_is_actually_used():
    assert any(ACCENT.lower() in s.lower() for s in SVGS.values())


# ───────────────────────── toolkit ─────────────────────────
def test_toolkit_has_exactly_the_agreed_12_tools():
    root = ET.fromstring(SVGS["toolkit"])
    labels = [el.text for el in root.iter() if el.tag.endswith("text") and "tool-label" in (el.get("class") or "")]
    assert labels == TOOLKIT


def test_toolkit_logos_are_marked_as_logos():
    root = ET.fromstring(SVGS["toolkit"])
    logos = [el for el in root.iter() if "logo" in (el.get("class") or "").split()]
    assert len(logos) == len(TOOLKIT)


# ───────────────────────── committed assets in sync ─────────────────────────
@pytest.mark.parametrize("name", sorted(PANELS))
def test_committed_panel_matches_generator_and_readme(name):
    digest = hashlib.sha1(PANELS[name]().encode()).hexdigest()[:8]
    fname = f"{name}.{digest}.svg"
    assert (ROOT / "assets" / fname).exists(), f"assets/{fname} missing: run python scripts/panels.py"
    assert f"./assets/{fname}" in (ROOT / "README.md").read_text()


@pytest.mark.parametrize("name,fn", [("banner", banner.banner), ("footer", banner.footer)])
def test_committed_banner_assets_match_generator(name, fn):
    assert (ROOT / "assets" / f"{name}.svg").read_text() == fn()


# ───────────────────────── README ─────────────────────────
README = (ROOT / "README.md").read_text()
INTRO_START = "At Tradeify I build agents and agentic workflows"


def test_readme_has_plain_text_intro_under_the_role_strip():
    assert INTRO_START in README
    intro_line = next(l for l in README.splitlines() if l.startswith(INTRO_START))
    assert "<" not in intro_line, "intro must be plain markdown text, not HTML/image"
    sentences = [s for s in re.split(r"(?<=[.!?])\s+", intro_line.strip()) if s]
    assert 2 <= len(sentences) <= 3
    assert "MPTL" in intro_line and "harness" in intro_line
    assert README.index("assets/hero.") < README.index(INTRO_START) < README.index("contributions-dark.svg")


def test_readme_assets_exist():
    for ref in re.findall(r"\./assets/[\w.\-]+\.svg", README):
        assert (ROOT / ref).exists(), ref


def test_readme_shields_badges_use_one_accent():
    colours = []
    for url in re.findall(r"https://img\.shields\.io/badge/[^\"']+", README):
        path = url.split("?")[0].rsplit("/", 1)[-1]
        colours.append("#" + path.rsplit("-", 1)[-1])
        colours += ["#" + v for k, v in re.findall(r"(labelColor|logoColor)=([0-9a-fA-F]{6})", url)]
    for m in re.findall(r"komarev\.com/ghpvc/\?[^\"']*color=([0-9a-fA-F]{6})", README):
        colours.append("#" + m)
    off = sorted({c for c in colours if not is_on_palette(c)})
    assert not off, f"off-palette badge colours: {off}"


# ───────────────────────── workflow ─────────────────────────
def test_snake_palette_uses_accent():
    wf = (ROOT / ".github" / "workflows" / "snake.yml").read_text()
    colours = HEX.findall(" ".join(re.findall(r"github-snake[^\n]*", wf)))
    assert colours, "snake outputs should set explicit colours"
    off = sorted({norm(c) for c in colours if not is_on_palette(c)})
    assert not off, f"off-palette snake colours: {off}"


def test_workflow_runs_tests_before_publishing():
    wf = (ROOT / ".github" / "workflows" / "snake.yml").read_text()
    assert "pytest" in wf
    assert wf.index("pytest") < wf.index("ghaction-github-pages")
