"""Guards for the profile README. Run: python -m pytest -q"""
import pathlib
import re
import xml.etree.ElementTree as ET

import pytest

ROOT = pathlib.Path(__file__).resolve().parent.parent
README = (ROOT / "README.md").read_text()


def test_quote_panel_is_gone():
    assert "assets/quote." not in README
    assert "The model is the engine" not in README
    assert not list((ROOT / "assets").glob("quote*.svg"))
    assert '("quote", quote)' not in (ROOT / "scripts" / "panels.py").read_text()


def test_every_readme_asset_exists():
    for ref in re.findall(r"\./assets/[\w.\-]+\.svg", README):
        assert (ROOT / ref).exists(), ref


@pytest.mark.parametrize("path", sorted((ROOT / "assets").glob("*.svg")), ids=lambda p: p.name)
def test_assets_are_valid_standalone_svg(path):
    ET.fromstring(path.read_text())
