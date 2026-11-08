"""Builds a contributions card (dark + light SVG) and a shields.io endpoint JSON.

Runs inside GitHub Actions with GITHUB_TOKEN. Stdlib only.
Usage: python scripts/contrib_card.py <username> <out_dir>
       MOCK=1 python scripts/contrib_card.py <username> <out_dir>   (offline test data)
"""
import datetime as dt
import json
import os
import random
import sys
import urllib.request

API = "https://api.github.com/graphql"


def gql(query, variables):
    req = urllib.request.Request(
        API,
        data=json.dumps({"query": query, "variables": variables}).encode(),
        headers={
            "Authorization": f"bearer {os.environ['GITHUB_TOKEN']}",
            "Content-Type": "application/json",
            "User-Agent": "profile-contrib-card",
        },
    )
    with urllib.request.urlopen(req, timeout=30) as r:
        body = json.load(r)
    if body.get("errors"):
        raise RuntimeError(body["errors"])
    return body["data"]


def fetch_days(user):
    years = gql(
        "query($u:String!){user(login:$u){contributionsCollection{contributionYears}}}",
        {"u": user},
    )["user"]["contributionsCollection"]["contributionYears"]
    q = """query($u:String!,$f:DateTime!,$t:DateTime!){user(login:$u){
      contributionsCollection(from:$f,to:$t){contributionCalendar{
        weeks{contributionDays{date contributionCount}}}}}}"""
    days = {}
    for y in years:
        data = gql(q, {"u": user, "f": f"{y}-01-01T00:00:00Z", "t": f"{y}-12-31T23:59:59Z"})
        for w in data["user"]["contributionsCollection"]["contributionCalendar"]["weeks"]:
            for d in w["contributionDays"]:
                days[d["date"]] = d["contributionCount"]
    return days


def mock_days():
    random.seed(7)
    start, today = dt.date(2021, 3, 1), dt.date.today()
    out, d = {}, start
    while d <= today:
        out[d.isoformat()] = random.choice([0, 0, 1, 2, 3, 5, 8, 13])
        d += dt.timedelta(days=1)
    return out


def stats(days):
    today = dt.date.today()
    items = sorted((dt.date.fromisoformat(k), v) for k, v in days.items() if dt.date.fromisoformat(k) <= today)
    total = sum(v for _, v in items)
    this_year = sum(v for d, v in items if d.year == today.year)
    first = next((d for d, v in items if v > 0), today)
    best_day, best_n = max(items, key=lambda x: x[1]) if items else (today, 0)

    longest = run = 0
    for _, v in items:
        run = run + 1 if v > 0 else 0
        longest = max(longest, run)

    lookup = dict(items)
    cur, d = 0, today
    if lookup.get(d, 0) == 0:  # today not counted yet doesn't break the streak
        d -= dt.timedelta(days=1)
    while lookup.get(d, 0) > 0:
        cur += 1
        d -= dt.timedelta(days=1)

    active = sum(1 for _, v in items if v > 0)
    return {
        "total": total, "this_year": this_year, "year": today.year, "since": first,
        "current": cur, "longest": longest, "best_n": best_n, "best_day": best_day,
        "active_days": active,
    }


THEMES = {
    "dark": dict(bg="#0d1117", border="#30363d", title="#8b949e", text="#e6edf3",
                 muted="#8b949e", accent="#58a6ff", accent2="#a371f7", ok="#3fb950", bar="#161b22"),
    "light": dict(bg="#ffffff", border="#d0d7de", title="#57606a", text="#1f2328",
                  muted="#57606a", accent="#0969da", accent2="#8250df", ok="#1a7f37", bar="#f6f8fa"),
}


def svg(s, user, t):
    fmt = lambda n: f"{n:,}"
    font = "'JetBrains Mono','SFMono-Regular',ui-monospace,Menlo,Consolas,monospace"
    since = s["since"].strftime("%b %Y")
    stats_cells = [
        ("current streak", f"{s['current']}d", t["ok"]),
        ("longest streak", f"{s['longest']}d", t["accent2"]),
        (f"in {s['year']}", fmt(s["this_year"]), t["accent"]),
        ("active days", fmt(s["active_days"]), t["text"]),
    ]
    cells = []
    for i, (label, val, col) in enumerate(stats_cells):
        x = 470 + (i % 2) * 165
        y = 92 + (i // 2) * 62
        delay = 0.5 + i * 0.12
        cells.append(
            f'<g class="fade" style="animation-delay:{delay:.2f}s">'
            f'<text x="{x}" y="{y}" fill="{col}" font-size="24" font-weight="700">{val}</text>'
            f'<text x="{x}" y="{y + 20}" fill="{t["muted"]}" font-size="12">{label}</text></g>'
        )
    return f'''<svg xmlns="http://www.w3.org/2000/svg" width="800" height="210" viewBox="0 0 800 210" role="img" aria-label="{fmt(s['total'])} GitHub contributions">
<style>
  text {{ font-family: {font}; }}
  .fade {{ animation: in .6s ease-out both; }}
  .big {{ animation: pop .8s cubic-bezier(.2,.9,.3,1.3) .2s both; transform-origin: 40px 120px; }}
  .cursor {{ animation: blink 1s steps(1) infinite; }}
  @keyframes in {{ from {{ opacity: 0; transform: translateY(6px); }} to {{ opacity: 1; transform: none; }} }}
  @keyframes pop {{ from {{ opacity: 0; transform: scale(.85); }} to {{ opacity: 1; transform: none; }} }}
  @keyframes blink {{ 50% {{ opacity: 0; }} }}
</style>
<defs>
  <linearGradient id="g" x1="0" x2="1"><stop offset="0" stop-color="{t['accent']}"/><stop offset="1" stop-color="{t['accent2']}"/></linearGradient>
</defs>
<rect x=".5" y=".5" width="799" height="209" rx="10" fill="{t['bg']}" stroke="{t['border']}"/>
<rect x=".5" y=".5" width="799" height="30" rx="10" fill="{t['bar']}"/>
<rect x=".5" y="20" width="799" height="11" fill="{t['bar']}"/>
<line x1="0" y1="30.5" x2="800" y2="30.5" stroke="{t['border']}"/>
<circle cx="20" cy="15.5" r="5" fill="#ff5f57"/><circle cx="38" cy="15.5" r="5" fill="#febc2e"/><circle cx="56" cy="15.5" r="5" fill="#28c840"/>
<text x="400" y="20" text-anchor="middle" fill="{t['title']}" font-size="12">{user}@github: ~/contributions</text>
<text x="40" y="58" fill="{t['muted']}" font-size="13"><tspan fill="{t['ok']}">$</tspan> git rev-list --count --all --author={user}<tspan class="cursor" fill="{t['text']}">▋</tspan></text>
<g class="big"><text x="38" y="132" fill="url(#g)" font-size="64" font-weight="800">{fmt(s['total'])}</text></g>
<text class="fade" style="animation-delay:.45s" x="40" y="160" fill="{t['text']}" font-size="14">contributions since {since}</text>
<text class="fade" style="animation-delay:.6s" x="40" y="182" fill="{t['muted']}" font-size="12">peak day: {s['best_n']} on {s['best_day'].strftime('%d %b %Y')}</text>
<line x1="440" y1="76" x2="440" y2="186" stroke="{t['border']}"/>
{''.join(cells)}
</svg>'''


def main():
    user, out = sys.argv[1], sys.argv[2]
    os.makedirs(out, exist_ok=True)
    days = mock_days() if os.environ.get("MOCK") else fetch_days(user)
    s = stats(days)
    for name, theme in THEMES.items():
        suffix = "-dark" if name == "dark" else ""
        with open(os.path.join(out, f"contributions{suffix}.svg"), "w") as f:
            f.write(svg(s, user, theme))
    with open(os.path.join(out, "contributions.json"), "w") as f:
        json.dump({"schemaVersion": 1, "label": "contributions", "message": f"{s['total']:,}",
                   "color": "58a6ff", "labelColor": "0d1117", "style": "flat-square"}, f)
    print(json.dumps({k: str(v) for k, v in s.items()}))


if __name__ == "__main__":
    main()
