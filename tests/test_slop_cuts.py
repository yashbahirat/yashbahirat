"""Each removed gimmick stays removed: generators, committed assets and README. Run: python -m pytest -q"""
import hashlib
import pathlib
import sys

import pytest

ROOT = pathlib.Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "scripts"))
import banner  # noqa: E402
import contrib_card  # noqa: E402
import panels  # noqa: E402

S = contrib_card.stats(contrib_card.mock_days())
CARD = {t: contrib_card.svg(S, "yashbahirat", contrib_card.THEMES[t]) for t in ("dark", "light")}
README = (ROOT / "README.md").read_text()


def committed(name):
    digest = hashlib.sha1(getattr(panels, name if name != "toolkit" else "tools")().encode()).hexdigest()[:8]
    return (ROOT / "assets" / f"{name}.{digest}.svg").read_text()


# 1 · banner prompt
def test_banner_has_no_fake_prompt():
    for svg in (banner.banner(), (ROOT / "assets" / "banner.svg").read_text()):
        assert "./boot" not in svg and "~/yash" not in svg


# 9 · banner ring text (loop stays)
def test_banner_ring_text_gone_but_loop_stays():
    svg = banner.banner()
    assert "textPath" not in svg and "RETRIES" not in svg
    for node in ("context", "tools", "evals", "retries", "model"):
        assert f">{node}<" in svg


# 2 + 3 · contributions card
@pytest.mark.parametrize("theme", ["dark", "light"])
def test_card_has_no_fake_command_or_peak_day(theme):
    svg = CARD[theme]
    assert "git rev-list" not in svg
    assert "peak day" not in svg
    assert f"{S['total']:,}" in svg and "contributions since" in svg


# 5 + 6 · agent.yaml
def test_agent_yaml_gags_and_beliefs_gone():
    for svg in (panels.agent(), committed("agent")):
        for gone in ("hallucination", "NORMAL", "context is a budget", "evaluated, it doesn", "spend it like money"):
            assert gone not in svg, gone
        for kept in ("focus", "harness_engineering", "research", "Harmony-Bot"):
            assert kept in svg, kept


# 7 · footer removed entirely
def test_footer_is_gone():
    assert "footer" not in README
    assert "open to" not in README
    assert not (ROOT / "assets" / "footer.svg").exists()
    assert "def footer" not in (ROOT / "scripts" / "banner.py").read_text()


def test_page_ends_on_contact_links():
    tail = README.strip().splitlines()[-3:]
    assert any("linkedin.com/in/yashbahirat" in l for l in tail)


# 8 · honest status
def test_regulos_is_built_not_shipped():
    for svg in (panels.projects(), committed("projects")):
        assert "shipped" not in svg
        assert ">built<" in svg


# 4 was not requested: badge row untouched
def test_badge_row_untouched():
    assert "badge/status-shipping" in README and "badge/harness-claude--code" in README


def test_agent_yaml_has_no_double_blank_lines():
    assert "\n\n\n" not in panels.AGENT_YAML


BELIEFS = ["a memory without a source is a rumor",
           "agents fail quietly. harnesses should fail loudly",
           "temperature 0 is not a test suite"]


def test_agent_yaml_has_exactly_the_three_chosen_beliefs():
    y = panels.AGENT_YAML
    block = y[y.index("  beliefs:"):y.index("  research:")]
    assert [l.strip()[3:-1] for l in block.splitlines()[1:] if l.strip()] == BELIEFS
    assert y.index("focus:") < y.index("beliefs:") < y.index("research:")
    svg = committed("agent")
    for b in BELIEFS:
        assert b in svg.replace("&#x27;", "'"), b


@pytest.mark.parametrize("theme", ["dark", "light"])
def test_card_has_no_bar_chart(theme):
    svg = CARD[theme]
    assert 'class="grow"' not in svg and "last 60 days" not in svg and ">today<" not in svg
    h = int(__import__("re").search(r'height="(\d+)"', svg).group(1))
    assert h <= 210, "card should shrink once the chart is gone"
    for kept in ("current streak", "longest streak", "last 30 days", "contributions since"):
        assert kept in svg, kept
