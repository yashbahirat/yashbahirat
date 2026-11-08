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
    W, H = 800, 300
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

    # 60-day activity bars, sqrt-scaled so one huge day doesn't flatten the rest
    series = s["last60"]
    peak = max(series) or 1
    base, maxh, x0, pitch, bw = 262, 50, 40, 12, 8
    bars = []
    for i, v in enumerate(series):
        h = 2 if v == 0 else max(4, maxh * math.sqrt(v / peak))
        fill = t["border"] if v == 0 else "url(#bar)"
        bars.append(
            f'<rect class="grow" style="animation-delay:{0.7 + i * 0.012:.3f}s" x="{x0 + i * pitch}" '
            f'y="{base - h:.1f}" width="{bw}" height="{h:.1f}" rx="2" fill="{fill}"/>'
        )

    return f'''<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" viewBox="0 0 {W} {H}" role="img" aria-label="{fmt(s['total'])} GitHub contributions">
<style>
  {font_face("JBM", "jbmono-500.woff2", 500)}
  {font_face("JBM", "jbmono-800.woff2", 800)}
  text {{ font-family: {font}; }}
  .fade {{ animation: in .6s ease-out both; }}
  .big {{ animation: pop .8s cubic-bezier(.2,.9,.3,1.3) .2s both; transform-origin: 40px 120px; }}
  .grow {{ animation: grow .7s cubic-bezier(.2,.8,.2,1) both; transform-box: fill-box; transform-origin: bottom; }}
  .cursor {{ animation: blink 1s steps(1) infinite; }}
  @keyframes in {{ from {{ opacity: 0; transform: translateY(6px); }} to {{ opacity: 1; transform: none; }} }}
  @keyframes pop {{ from {{ opacity: 0; transform: scale(.85); }} to {{ opacity: 1; transform: none; }} }}
  @keyframes grow {{ from {{ transform: scaleY(0); }} to {{ transform: none; }} }}
  @keyframes blink {{ 50% {{ opacity: 0; }} }}
</style>
<defs>
  <linearGradient id="g" x1="0" x2="1"><stop offset="0" stop-color="{t['accent']}"/><stop offset="1" stop-color="{t['accent2']}"/></linearGradient>
  <linearGradient id="bar" x1="0" y1="1" x2="0" y2="0"><stop offset="0" stop-color="{t['accent']}"/><stop offset="1" stop-color="{t['accent2']}"/></linearGradient>
</defs>
<rect x=".5" y=".5" width="{W - 1}" height="{H - 1}" rx="10" fill="{t['bg']}" stroke="{t['border']}"/>
<rect x=".5" y=".5" width="{W - 1}" height="30" rx="10" fill="{t['bar']}"/>
<rect x=".5" y="20" width="{W - 1}" height="11" fill="{t['bar']}"/>
<line x1="0" y1="30.5" x2="{W}" y2="30.5" stroke="{t['border']}"/>
<circle cx="20" cy="15.5" r="5" fill="#ff5f57"/><circle cx="38" cy="15.5" r="5" fill="#febc2e"/><circle cx="56" cy="15.5" r="5" fill="#28c840"/>
<text x="{W / 2}" y="20" text-anchor="middle" fill="{t['title']}" font-size="12">{user}@github: ~/contributions</text>
<text x="40" y="58" fill="{t['muted']}" font-size="13"><tspan fill="{t['ok']}">$</tspan> git rev-list --count --all --author={user}<tspan class="cursor" fill="{t['text']}">▋</tspan></text>
<g class="big"><text x="38" y="132" fill="url(#g)" font-size="64" font-weight="800">{fmt(s['total'])}</text></g>
<text class="fade" style="animation-delay:.45s" x="40" y="160" fill="{t['text']}" font-size="14">contributions since {since}</text>
<text class="fade" style="animation-delay:.6s" x="40" y="182" fill="{t['muted']}" font-size="12">peak day: {fmt(s['best_n'])} on {s['best_day'].strftime('%d %b %Y')}</text>
<line x1="440" y1="76" x2="440" y2="186" stroke="{t['border']}"/>
{''.join(cells)}
<line x1="40" y1="202" x2="{W - 40}" y2="202" stroke="{t['border']}" stroke-dasharray="2 4"/>
{''.join(bars)}
<text x="40" y="284" fill="{t['muted']}" font-size="11">last 60 days</text>
<text x="{W - 40}" y="284" text-anchor="end" fill="{t['muted']}" font-size="11">today</text>
</svg>'''


PHRASES = [
    "harness engineering > prompt engineering",
    "building agents that remember what they did, and why",
    "junior agentic coder @ tradeify",
    "research. build. eval. repeat.",
]


def hero_svg(s):
    """Typing terminal line + live stat chips. Always dark, to sit under the banner."""
    W, H, BG = 1280, 150, "#05070d"
    font = "'JBM',ui-monospace,Menlo,Consolas,monospace"
    size, cw = 22, 22 * 0.6
    x0 = 48 + len("yash@agentic:~$ ") * cw
    n, T = len(PHRASES), 5.0 * len(PHRASES)
    css, groups = [], []
    for i, ph in enumerate(PHRASES):
        L = len(ph) * cw
        a, b, c, d, e = [100 * (i + f) / n for f in (0, 0.42, 0.80, 0.94, 1)]
        css.append(
            (f"@keyframes v{i}{{0%,{e - 0.01:.3f}%{{opacity:1}}{e:.3f}%,100%{{opacity:0}}}}" if i == 0 else
             f"@keyframes v{i}{{0%,{a - 0.01:.3f}%{{opacity:0}}{a:.3f}%,{e - 0.01:.3f}%{{opacity:1}}{e:.3f}%,100%{{opacity:0}}}}") +
            f"@keyframes t{i}{{0%,{a:.3f}%{{transform:translateX(0);animation-timing-function:steps({len(ph)},end)}}"
            f"{b:.3f}%{{transform:translateX({L:.1f}px)}}"
            f"{c:.3f}%{{transform:translateX({L:.1f}px);animation-timing-function:steps({len(ph)},end)}}"
            f"{d:.3f}%,100%{{transform:translateX(0)}}}}"
            f".v{i}{{opacity:0;animation:v{i} {T}s linear infinite}}"
            f".t{i}{{animation:t{i} {T}s linear infinite}}"
        )
        groups.append(
            f'<g class="v{i}"><text x="{x0:.1f}" y="62" font-size="{size}" fill="#e6edf3">{ph}</text>'
            f'<rect class="t{i}" x="{x0:.1f}" y="36" width="{L + 16:.1f}" height="34" fill="{BG}"/>'
            f'<rect class="t{i}" x="{x0 + 1:.1f}" y="43" width="11" height="24" rx="1.5" fill="#58a6ff"/></g>'
        )

    chips_data = [
        (f"{s['total']:,}", "contributions", "#58a6ff"),
        (f"{s['current']}d", "streak", "#3fb950"),
        ("claude-code", "harness", "#d97757"),
        ("1 paper", "1 patent", "#bc8cff"),
        ("CSE-AI", "VIT Pune", "#8b949e"),
    ]
    chips, x = [], 48
    for i, (val, label, col) in enumerate(chips_data):
        w = 34 + 8.4 * len(val) + 7.8 * len(label) + 8
        chips.append(
            f'<g class="chip" style="animation-delay:{0.15 + i * 0.1:.2f}s">'
            f'<rect x="{x}" y="96" width="{w:.1f}" height="32" rx="16" fill="#0d1117" stroke="#21262d"/>'
            f'<circle cx="{x + 17}" cy="112" r="4" fill="{col}"/>'
            f'<text x="{x + 29}" y="117" font-size="14" font-weight="800" fill="#e6edf3">{val}'
            f'<tspan font-weight="500" font-size="13" fill="#8b949e" dx="8">{label}</tspan></text></g>'
        )
        x += w + 10

    return f'''<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" viewBox="0 0 {W} {H}" role="img" aria-label="{' / '.join(PHRASES)}">
<style>
  {font_face("JBM", "jbmono-500.woff2", 500)}
  {font_face("JBM", "jbmono-800.woff2", 800)}
  text {{ font-family: {font}; }}
  .chip {{ animation: chip .6s cubic-bezier(.2,.8,.2,1) both; }}
  .live {{ animation: live 1.8s ease-in-out infinite; transform-box: fill-box; transform-origin: center; }}
  @keyframes chip {{ from {{ opacity: 0; transform: translateY(8px); }} to {{ opacity: 1; transform: none; }} }}
  @keyframes live {{ 0% {{ transform: scale(1); opacity: .9; }} 100% {{ transform: scale(2.6); opacity: 0; }} }}
  {"".join(css)}
</style>
<defs>
  <clipPath id="c"><rect width="{W}" height="{H}" rx="16"/></clipPath>
  <linearGradient id="edge" x1="0" x2="1"><stop offset="0" stop-color="#58a6ff" stop-opacity="0"/><stop offset=".5" stop-color="#bc8cff"/><stop offset="1" stop-color="#58a6ff" stop-opacity="0"/></linearGradient>
  <radialGradient id="glow"><stop offset="0" stop-color="#8957e5" stop-opacity=".28"/><stop offset="1" stop-color="#8957e5" stop-opacity="0"/></radialGradient>
</defs>
<g clip-path="url(#c)">
  <rect width="{W}" height="{H}" fill="{BG}"/>
  <ellipse cx="{W - 120}" cy="{H + 30}" rx="380" ry="100" fill="url(#glow)"/>
  <rect width="{W}" height="1.5" fill="url(#edge)"/>
  <text x="48" y="62" font-size="{size}"><tspan fill="#3fb950">yash</tspan><tspan fill="#6e7681">@</tspan><tspan fill="#bc8cff">agentic</tspan><tspan fill="#6e7681">:</tspan><tspan fill="#58a6ff">~</tspan><tspan fill="#6e7681">$ </tspan></text>
  {"".join(groups)}
  <circle cx="{W - 120}" cy="54" r="4" fill="#3fb950"/><circle cx="{W - 120}" cy="54" r="4" fill="#3fb950" class="live"/>
  <text x="{W - 108}" y="59" font-size="13" fill="#8b949e">online</text>
  <line x1="48" y1="82" x2="{W - 48}" y2="82" stroke="#21262d" stroke-dasharray="2 5"/>
  {"".join(chips)}
</g>
<rect x=".5" y=".5" width="{W - 1}" height="{H - 1}" rx="16" fill="none" stroke="#21262d"/>
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
    with open(os.path.join(out, "hero.svg"), "w") as f:
        f.write(hero_svg(s))
    with open(os.path.join(out, "contributions.json"), "w") as f:
        json.dump({"schemaVersion": 1, "label": "contributions", "message": f"{s['total']:,}",
                   "color": "58a6ff", "labelColor": "0d1117", "style": "flat-square"}, f)
    print(json.dumps({k: str(v) for k, v in s.items()}))


if __name__ == "__main__":
    main()
