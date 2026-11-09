"""Builds a contributions card (dark + light SVG) and a shields.io endpoint JSON.

Runs inside GitHub Actions with GITHUB_TOKEN. Stdlib only.
Usage: python scripts/contrib_card.py <username> <out_dir>
       MOCK=1 python scripts/contrib_card.py <username> <out_dir>   (offline test data)
"""
import base64
import datetime as dt
import math
import pathlib
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
    last60 = [lookup.get(today - dt.timedelta(days=i), 0) for i in range(59, -1, -1)]
    return {
        "last30": sum(last60[-30:]), "last60": last60,
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


def font_face(family, file, weight):
    path = pathlib.Path(__file__).resolve().parent.parent / "assets" / "fonts" / file
    if not path.exists():
        return ""
    data = base64.b64encode(path.read_bytes()).decode()
    return (f"@font-face{{font-family:'{family}';font-weight:{weight};"
            f"src:url(data:font/woff2;base64,{data}) format('woff2');}}")


def svg(s, user, t):
    fmt = lambda n: f"{n:,}"
    font = "'JBM','SFMono-Regular',ui-monospace,Menlo,Consolas,monospace"
    since = s["since"].strftime("%b %Y")
    W, H = 800, 200
    stats_cells = [
        ("current streak", f"{s['current']}d", t["ok"]),
        ("longest streak", f"{s['longest']}d", t["accent2"]),
        (f"in {s['year']}", fmt(s["this_year"]), t["accent"]),
        ("last 30 days", fmt(s["last30"]), t["text"]),
    ]
    cells = []
    for i, (label, val, col) in enumerate(stats_cells):
        x = 470 + (i % 2) * 165
        y = 92 + (i // 2) * 62
        cells.append(
            f'<g class="fade" style="animation-delay:{0.5 + i * 0.12:.2f}s">'
            f'<text x="{x}" y="{y}" fill="{col}" font-size="24" font-weight="800">{val}</text>'
            f'<text x="{x}" y="{y + 20}" fill="{t["muted"]}" font-size="12">{label}</text></g>'
        )

    return f'''<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" viewBox="0 0 {W} {H}" role="img" aria-label="{fmt(s['total'])} GitHub contributions">
<style>
  {font_face("JBM", "jbmono-500.woff2", 500)}
  {font_face("JBM", "jbmono-800.woff2", 800)}
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
<rect x=".5" y=".5" width="{W - 1}" height="{H - 1}" rx="10" fill="{t['bg']}" stroke="{t['border']}"/>
<rect x=".5" y=".5" width="{W - 1}" height="30" rx="10" fill="{t['bar']}"/>
<rect x=".5" y="20" width="{W - 1}" height="11" fill="{t['bar']}"/>
<line x1="0" y1="30.5" x2="{W}" y2="30.5" stroke="{t['border']}"/>
<circle cx="20" cy="15.5" r="5" fill="#ff5f57"/><circle cx="38" cy="15.5" r="5" fill="#febc2e"/><circle cx="56" cy="15.5" r="5" fill="#28c840"/>
<text x="{W / 2}" y="20" text-anchor="middle" fill="{t['title']}" font-size="12">{user}@github: ~/contributions</text>
<g class="big"><text x="38" y="122" fill="url(#g)" font-size="64" font-weight="800">{fmt(s['total'])}</text></g>
<text class="fade" style="animation-delay:.45s" x="40" y="152" fill="{t['text']}" font-size="14">contributions since {since}</text>
<line x1="440" y1="76" x2="440" y2="186" stroke="{t['border']}"/>
{''.join(cells)}
</svg>'''


GH_LOGO = ("M12 .297c-6.63 0-12 5.373-12 12 0 5.303 3.438 9.8 8.205 11.385.6.113.82-.258.82-.577 0-.285-.01-1.04-.015-2.04-3.338.724-4.042-1.61-4.042-1.61"
           "C4.422 18.07 3.633 17.7 3.633 17.7c-1.087-.744.084-.729.084-.729 1.205.084 1.838 1.236 1.838 1.236 1.07 1.835 2.809 1.305 3.495.998.108-.776.417-1.305.76-1.605"
           "-2.665-.3-5.466-1.332-5.466-5.93 0-1.31.465-2.38 1.235-3.22-.135-.303-.54-1.523.105-3.176 0 0 1.005-.322 3.3 1.23.96-.267 1.98-.399 3-.405 1.02.006 2.04.138 3 .405"
           " 2.28-1.552 3.285-1.23 3.285-1.23.645 1.653.24 2.873.12 3.176.765.84 1.23 1.91 1.23 3.22 0 4.61-2.805 5.625-5.475 5.92.42.36.81 1.096.81 2.22 0 1.606-.015 2.896-.015 3.286"
           " 0 .315.21.69.825.57C20.565 22.092 24 17.592 24 12.297c0-6.627-5.373-12-12-12")

VERDANA_11 = {**{d: 7.0 for d in "0123456789"}, ",": 3.5, ".": 3.5, " ": 3.9,
              "a": 6.7, "b": 6.8, "c": 5.7, "d": 6.8, "e": 6.6, "f": 3.8, "g": 6.8, "h": 7.0, "i": 3.0,
              "j": 3.7, "k": 6.4, "l": 3.0, "m": 10.7, "n": 7.0, "o": 6.7, "p": 6.8, "q": 6.8, "r": 4.7,
              "s": 5.7, "t": 4.3, "u": 7.0, "v": 6.4, "w": 9.0, "x": 6.4, "y": 6.4, "z": 5.7}


def text_w(t):
    return sum(VERDANA_11.get(ch, 7.0) for ch in t)


def badge_svg(label, message, color="#58a6ff", label_bg="#0d1117"):
    """shields.io flat-square look-alike with a GitHub logo; no third-party service involved."""
    lw_text, mw_text = text_w(label), text_w(message)
    lw = 5 + 14 + 4 + lw_text + 5
    mw = 5 + mw_text + 5
    W = lw + mw
    font = "Verdana,Geneva,DejaVu Sans,sans-serif"
    return f"""<svg xmlns="http://www.w3.org/2000/svg" width="{W:.0f}" height="20" viewBox="0 0 {W:.1f} 20" role="img" aria-label="{label}: {message}">
<title>{label}: {message}</title>
<g shape-rendering="crispEdges"><rect width="{lw:.1f}" height="20" fill="{label_bg}"/><rect x="{lw:.1f}" width="{mw:.1f}" height="20" fill="{color}"/></g>
<path transform="translate(5 3) scale(.5833)" fill="#ffffff" d="{GH_LOGO}"/>
<g fill="#fff" font-family="{font}" font-size="11" text-rendering="geometricPrecision">
<text x="{23:.1f}" y="14" textLength="{lw_text:.1f}">{label}</text>
<text x="{lw + 5:.1f}" y="14" textLength="{mw_text:.1f}">{message}</text>
</g></svg>"""


def main():
    user, out = sys.argv[1], sys.argv[2]
    os.makedirs(out, exist_ok=True)
    days = mock_days() if os.environ.get("MOCK") else fetch_days(user)
    s = stats(days)
    for name, theme in THEMES.items():
        suffix = "-dark" if name == "dark" else ""
        with open(os.path.join(out, f"contributions{suffix}.svg"), "w") as f:
            f.write(svg(s, user, theme))
    with open(os.path.join(out, "contributions-badge.svg"), "w") as f:
        f.write(badge_svg("contributions", f"{s['total']:,}"))
    with open(os.path.join(out, "contributions.json"), "w") as f:
        json.dump({"schemaVersion": 1, "label": "contributions", "message": f"{s['total']:,}",
                   "color": "58a6ff", "labelColor": "0d1117", "style": "flat-square"}, f)
    print(json.dumps({k: str(v) for k, v in s.items()}))


if __name__ == "__main__":
    main()
