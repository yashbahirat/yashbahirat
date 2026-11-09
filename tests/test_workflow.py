"""Guards for the card-refresh workflow. Run: python -m pytest -q"""
import pathlib
import re

WF = (pathlib.Path(__file__).resolve().parent.parent / ".github" / "workflows" / "snake.yml").read_text()


def cron():
    m = re.search(r'cron:\s*"([^"]+)"', WF)
    assert m, "workflow needs a schedule"
    return m.group(1).split()


def test_schedule_avoids_top_of_hour():
    # GitHub delays or drops scheduled runs at minute 0 under load; this one never fired.
    assert cron()[0] != "0"


def test_schedule_runs_at_least_every_6_hours():
    hour = cron()[1]
    step = re.fullmatch(r"\*/(\d+)", hour)
    assert step and int(step.group(1)) <= 6


def test_can_still_run_manually_and_on_push():
    assert "workflow_dispatch:" in WF and "push:" in WF
