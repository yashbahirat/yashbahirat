"""Generates assets/banner.svg and assets/footer.svg with embedded subset fonts.

Usage: python scripts/banner.py   (run from repo root)
"""
import base64
import math
import pathlib

ROOT = pathlib.Path(__file__).resolve().parent.parent
FONTS = ROOT / "assets" / "fonts"


def font_face(family, file, weight):
    data = base64.b64encode((FONTS / file).read_bytes()).decode()
    return (f"@font-face{{font-family:'{family}';font-weight:{weight};"
            f"src:url(data:font/woff2;base64,{data}) format('woff2');}}")


W, H = 1280, 380
CX, CY, R = 1010, 190, 100           # agent loop centre + radius
RING = 150                           # harness ring radius

MONO = "'JBM',ui-monospace,Menlo,Consolas,monospace"
DISPLAY = "'Unb','Arial Black',sans-serif"


def node(label, angle_deg, delay):
    a = math.radians(angle_deg)
    x, y = CX + R * math.cos(a), CY + R * math.sin(a)
    w = 14 + 8.4 * len(label)
    return f'''
  <g class="pop" style="animation-delay:{delay}s">
    <rect x="{x - w / 2:.1f}" y="{y - 14:.1f}" width="{w:.1f}" height="28" rx="14" fill="#0d1117" stroke="url(#edge)" stroke-width="1.2"/>
    <text x="{x:.1f}" y="{y + 4.5:.1f}" text-anchor="middle" font-family="{MONO}" font-size="13" fill="#c9d1d9">{label}</text>
  </g>'''


def banner():
    loop = (f"M {CX} {CY - R} A {R} {R} 0 1 1 {CX - 0.01} {CY - R} Z")
    spokes = "".join(
        f'<line x1="{CX}" y1="{CY}" x2="{CX + (R - 16) * math.cos(math.radians(a)):.1f}" '
        f'y2="{CY + (R - 16) * math.sin(math.radians(a)):.1f}" class="spoke"/>'
        for a in (-90, 0, 90, 180)
    )
    nodes = "".join(node(l, a, d) for l, a, d in (
        ("plan", -90, 0.5), ("act", 0, 0.65), ("observe", 90, 0.8), ("reflect", 180, 0.95)))

    return f'''<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" viewBox="0 0 {W} {H}" role="img" aria-label="Yash Bahirat: agent, harness and inference engineering">
<style>
  {font_face("Unb", "unbounded-800.woff2", 800)}
  {font_face("JBM", "jbmono-500.woff2", 500)}
  .rise {{ animation: rise 1s cubic-bezier(.2,.8,.2,1) both; }}
  .pop  {{ animation: pop .7s cubic-bezier(.2,.9,.3,1.4) both; transform-box: fill-box; transform-origin: center; }}
  .flow {{ fill: none; stroke: url(#edge); stroke-width: 1.6; stroke-dasharray: 6 10; animation: flow 1.4s linear infinite; }}
  .spoke {{ stroke: #30363d; stroke-width: 1; stroke-dasharray: 2 6; animation: flow 2.4s linear infinite reverse; }}
  .spin {{ animation: spin 60s linear infinite; transform-origin: {CX}px {CY}px; }}
  .drift1 {{ animation: drift 14s ease-in-out infinite alternate; }}
  .drift2 {{ animation: drift 18s ease-in-out infinite alternate-reverse; }}
  .blink {{ animation: blink 1.05s steps(1) infinite; }}
  .pulse {{ animation: pulse 2.4s ease-in-out infinite; transform-box: fill-box; transform-origin: center; }}
  @keyframes rise  {{ from {{ opacity: 0; transform: translateY(14px); }} to {{ opacity: 1; transform: none; }} }}
  @keyframes pop   {{ from {{ opacity: 0; transform: scale(.6); }} to {{ opacity: 1; transform: none; }} }}
  @keyframes flow  {{ to {{ stroke-dashoffset: -32; }} }}
  @keyframes spin  {{ to {{ transform: rotate(360deg); }} }}
  @keyframes drift {{ to {{ transform: translate(60px, 24px); }} }}
  @keyframes blink {{ 50% {{ opacity: 0; }} }}
  @keyframes pulse {{ 50% {{ transform: scale(1.12); opacity: .75; }} }}
</style>
<defs>
  <clipPath id="clip"><rect width="{W}" height="{H}" rx="18"/></clipPath>
  <radialGradient id="g1"><stop offset="0" stop-color="#1f6feb" stop-opacity=".55"/><stop offset="1" stop-color="#1f6feb" stop-opacity="0"/></radialGradient>
  <radialGradient id="g2"><stop offset="0" stop-color="#8957e5" stop-opacity=".5"/><stop offset="1" stop-color="#8957e5" stop-opacity="0"/></radialGradient>
  <radialGradient id="g3"><stop offset="0" stop-color="#2ea043" stop-opacity=".09"/><stop offset="1" stop-color="#2ea043" stop-opacity="0"/></radialGradient>
  <radialGradient id="fade" cx=".5" cy=".5" r=".65"><stop offset="0" stop-color="#fff"/><stop offset="1" stop-color="#000"/></radialGradient>
  <mask id="gridmask"><rect width="{W}" height="{H}" fill="url(#fade)"/></mask>
  <pattern id="dots" width="22" height="22" patternUnits="userSpaceOnUse"><circle cx="1.2" cy="1.2" r="1.2" fill="#c9d1d9"/></pattern>
  <linearGradient id="name" x1="80" y1="0" x2="640" y2="0" gradientUnits="userSpaceOnUse">
    <stop offset="0" stop-color="#ffffff"/><stop offset=".55" stop-color="#a5d6ff"/><stop offset="1" stop-color="#d2a8ff"/>
  </linearGradient>
  <linearGradient id="edge" x1="0" x2="1"><stop offset="0" stop-color="#58a6ff"/><stop offset="1" stop-color="#bc8cff"/></linearGradient>
  <linearGradient id="topline" x1="0" x2="1"><stop offset="0" stop-color="#58a6ff" stop-opacity="0"/><stop offset=".5" stop-color="#bc8cff"/><stop offset="1" stop-color="#58a6ff" stop-opacity="0"/></linearGradient>
  <filter id="glow" x="-20%" y="-40%" width="140%" height="180%"><feGaussianBlur stdDeviation="14"/></filter>
  <path id="loop" d="{loop}"/>
</defs>

<g clip-path="url(#clip)">
  <rect width="{W}" height="{H}" fill="#05070d"/>
  <g class="drift1"><circle cx="230" cy="40" r="420" fill="url(#g1)"/></g>
  <g class="drift2"><circle cx="1060" cy="330" r="380" fill="url(#g2)"/></g>
  <circle cx="640" cy="430" r="360" fill="url(#g3)"/>
  <rect width="{W}" height="{H}" fill="url(#dots)" opacity=".13" mask="url(#gridmask)"/>
  <rect x="0" y="0" width="{W}" height="1.5" fill="url(#topline)"/>
  <rect x="0" y="{H - 1.5}" width="{W}" height="1.5" fill="url(#topline)"/>

  <!-- left: identity -->
  <g class="rise" style="animation-delay:.18s">
    <text x="78" y="190" font-family="{DISPLAY}" font-weight="800" font-size="92" fill="#58a6ff" opacity=".35" filter="url(#glow)">YASH</text>
    <text x="78" y="190" font-family="{DISPLAY}" font-weight="800" font-size="92" fill="url(#name)">YASH</text>
  </g>
  <g class="rise" style="animation-delay:.3s">
    <text x="78" y="290" font-family="{DISPLAY}" font-weight="800" font-size="92" fill="#8957e5" opacity=".35" filter="url(#glow)">BAHIRAT</text>
    <text x="78" y="290" font-family="{DISPLAY}" font-weight="800" font-size="92" fill="url(#name)">BAHIRAT</text>
  </g>
  <g class="rise" style="animation-delay:.45s">
    <text x="82" y="336" font-family="{MONO}" font-size="15" fill="#8b949e">agent engineering <tspan fill="#58a6ff">/</tspan> harness engineering <tspan fill="#bc8cff">/</tspan> inference engineering</text>
  </g>

  <!-- right: the harness around the model -->
  <circle cx="{CX}" cy="{CY}" r="{R}" class="flow"/>
  {spokes}
  <circle r="4.5" fill="#e6edf3"><animateMotion dur="5s" repeatCount="indefinite" rotate="auto"><mpath href="#loop"/></animateMotion></circle>
  <circle r="11" fill="#58a6ff" opacity=".25"><animateMotion dur="5s" repeatCount="indefinite"><mpath href="#loop"/></animateMotion></circle>
  <g class="pop" style="animation-delay:.35s">
    <circle cx="{CX}" cy="{CY}" r="30" fill="#0d1117" stroke="url(#edge)" stroke-width="1.5"/>
    <circle cx="{CX}" cy="{CY}" r="30" fill="none" stroke="#58a6ff" stroke-opacity=".5" class="pulse"/>
    <text x="{CX}" y="{CY + 4.5}" text-anchor="middle" font-family="{MONO}" font-size="13" fill="#e6edf3">model</text>
  </g>
  {nodes}
</g>
<rect x=".5" y=".5" width="{W - 1}" height="{H - 1}" rx="18" fill="none" stroke="#21262d"/>
</svg>'''


def footer():
    w, h = 1280, 96
    return f'''<svg xmlns="http://www.w3.org/2000/svg" width="{w}" height="{h}" viewBox="0 0 {w} {h}" role="img" aria-label="open to: agent infra, eval tooling, research collabs">
<style>
  {font_face("JBM", "jbmono-500.woff2", 500)}
  .blink {{ animation: blink 1.05s steps(1) infinite; }}
  .scan {{ animation: scan 5s ease-in-out infinite; }}
  @keyframes blink {{ 50% {{ opacity: 0; }} }}
  @keyframes scan {{ 0% {{ transform: translateX(-400px); }} 100% {{ transform: translateX({w}px); }} }}
</style>
<defs>
  <clipPath id="c"><rect width="{w}" height="{h}" rx="14"/></clipPath>
  <linearGradient id="l" x1="0" x2="1"><stop offset="0" stop-color="#58a6ff" stop-opacity="0"/><stop offset=".5" stop-color="#bc8cff"/><stop offset="1" stop-color="#58a6ff" stop-opacity="0"/></linearGradient>
  <radialGradient id="g"><stop offset="0" stop-color="#8957e5" stop-opacity=".35"/><stop offset="1" stop-color="#8957e5" stop-opacity="0"/></radialGradient>
</defs>
<g clip-path="url(#c)">
  <rect width="{w}" height="{h}" fill="#05070d"/>
  <ellipse cx="{w / 2}" cy="{h}" rx="520" ry="90" fill="url(#g)"/>
  <rect y="0" width="{w}" height="1.5" fill="url(#l)"/>
  <rect class="scan" y="0" width="400" height="1.5" fill="#e6edf3" opacity=".6"/>
  <text x="{w / 2}" y="{h / 2 + 7}" text-anchor="middle" font-family="{MONO}" font-size="21" fill="#6e7681"><tspan fill="#3fb950">$</tspan> open to: <tspan fill="#e6edf3">agent infra</tspan> · <tspan fill="#e6edf3">eval tooling</tspan> · <tspan fill="#e6edf3">research collabs</tspan><tspan class="blink" fill="#e6edf3"> ▋</tspan></text>
</g>
<rect x=".5" y=".5" width="{w - 1}" height="{h - 1}" rx="14" fill="none" stroke="#21262d"/>
</svg>'''


if __name__ == "__main__":
    out = ROOT / "assets"
    (out / "banner.svg").write_text(banner())
    (out / "footer.svg").write_text(footer())
    print("wrote", out / "banner.svg", out / "footer.svg")
