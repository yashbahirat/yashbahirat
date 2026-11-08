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

ACCENT = "#F0883E"
MONO = "'JBM',ui-monospace,Menlo,Consolas,monospace"
DISPLAY = "'Unb','Arial Black',sans-serif"


def node(label, angle_deg, delay):
    a = math.radians(angle_deg)
    x, y = CX + R * math.cos(a), CY + R * math.sin(a)
    w = 14 + 8.4 * len(label)
    return f'''
  <g class="pop" style="animation-delay:{delay}s">
    <rect x="{x - w / 2:.1f}" y="{y - 14:.1f}" width="{w:.1f}" height="28" rx="14" fill="#0d1117" stroke="#30363d" stroke-width="1.2"/>
    <text x="{x:.1f}" y="{y + 4.5:.1f}" text-anchor="middle" font-family="{MONO}" font-size="13" fill="#c9d1d9">{label}</text>
  </g>'''


def banner():
    loop = (f"M {CX} {CY - R} A {R} {R} 0 1 1 {CX - 0.01} {CY - R} Z")
    ring = (f"M {CX} {CY - RING} A {RING} {RING} 0 1 1 {CX - 0.01} {CY - RING} Z")
    ring_text = "HARNESS · TOOLS · MEMORY · EVALS · CONTEXT · RETRIES · " * 2
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
  .flow {{ fill: none; stroke: {ACCENT}; stroke-width: 1.6; stroke-dasharray: 6 10; animation: flow 1.4s linear infinite; }}
  .spoke {{ stroke: #30363d; stroke-width: 1; stroke-dasharray: 2 6; animation: flow 2.4s linear infinite reverse; }}
  .spin {{ animation: spin 60s linear infinite; transform-origin: {CX}px {CY}px; }}
  .blink {{ animation: blink 1.05s steps(1) infinite; }}
  .pulse {{ animation: pulse 2.4s ease-in-out infinite; transform-box: fill-box; transform-origin: center; }}
  @keyframes rise  {{ from {{ opacity: 0; transform: translateY(14px); }} to {{ opacity: 1; transform: none; }} }}
  @keyframes pop   {{ from {{ opacity: 0; transform: scale(.6); }} to {{ opacity: 1; transform: none; }} }}
  @keyframes flow  {{ to {{ stroke-dashoffset: -32; }} }}
  @keyframes spin  {{ to {{ transform: rotate(360deg); }} }}
  @keyframes blink {{ 50% {{ opacity: 0; }} }}
  @keyframes pulse {{ 50% {{ transform: scale(1.12); opacity: .6; }} }}
</style>
<defs>
  <clipPath id="clip"><rect width="{W}" height="{H}" rx="18"/></clipPath>
  <pattern id="dots" width="22" height="22" patternUnits="userSpaceOnUse"><circle cx="1.2" cy="1.2" r="1.2" fill="#c9d1d9"/></pattern>
  <path id="ring" d="{ring}"/>
  <path id="loop" d="{loop}"/>
</defs>

<g clip-path="url(#clip)">
  <rect width="{W}" height="{H}" fill="#0a0c10"/>
  <rect width="{W}" height="{H}" fill="url(#dots)" opacity=".05"/>
  <rect x="0" y="0" width="{W}" height="2" fill="{ACCENT}"/>

  <!-- left: identity -->
  <g class="rise" style="animation-delay:.05s">
    <text x="82" y="86" font-family="{MONO}" font-size="15" fill="#8b949e"><tspan fill="{ACCENT}">●</tspan>  ~/yash <tspan fill="{ACCENT}">$</tspan> ./boot --agentic<tspan class="blink" fill="#e6edf3"> ▋</tspan></text>
  </g>
  <g class="rise" style="animation-delay:.18s">
    <text x="78" y="190" font-family="{DISPLAY}" font-weight="800" font-size="92" fill="#f0f6fc">YASH</text>
  </g>
  <g class="rise" style="animation-delay:.3s">
    <text x="78" y="290" font-family="{DISPLAY}" font-weight="800" font-size="92" fill="#f0f6fc">BAHIRAT</text>
  </g>
  <g class="rise" style="animation-delay:.45s">
    <text x="82" y="336" font-family="{MONO}" font-size="15" fill="#8b949e">agent engineering <tspan fill="{ACCENT}">/</tspan> harness engineering <tspan fill="{ACCENT}">/</tspan> inference engineering</text>
  </g>

  <!-- right: the harness around the model -->
  <g class="spin">
    <circle cx="{CX}" cy="{CY}" r="{RING}" fill="none" stroke="#21262d" stroke-width="1"/>
    <text font-family="{MONO}" font-size="10.5" letter-spacing="2.2" fill="#6e7681"><textPath href="#ring">{ring_text}</textPath></text>
  </g>
  <circle cx="{CX}" cy="{CY}" r="{R}" class="flow"/>
  {spokes}
  <circle r="4.5" fill="{ACCENT}"><animateMotion dur="5s" repeatCount="indefinite" rotate="auto"><mpath href="#loop"/></animateMotion></circle>
  <g class="pop" style="animation-delay:.35s">
    <circle cx="{CX}" cy="{CY}" r="30" fill="#0d1117" stroke="{ACCENT}" stroke-width="1.5"/>
    <circle cx="{CX}" cy="{CY}" r="30" fill="none" stroke="{ACCENT}" stroke-opacity=".45" class="pulse"/>
    <text x="{CX}" y="{CY + 4.5}" text-anchor="middle" font-family="{MONO}" font-size="13" fill="#e6edf3">model</text>
  </g>
  {nodes}
</g>
<rect x=".5" y=".5" width="{W - 1}" height="{H - 1}" rx="18" fill="none" stroke="#21262d"/>
</svg>'''


def footer():
    w, h = 1280, 96
    return f'''<svg xmlns="http://www.w3.org/2000/svg" width="{w}" height="{h}" viewBox="0 0 {w} {h}" role="img" aria-label="open to: agent infra, eval tooling, research collabs, hard problems">
<style>
  {font_face("JBM", "jbmono-500.woff2", 500)}
  .blink {{ animation: blink 1.05s steps(1) infinite; }}
  @keyframes blink {{ 50% {{ opacity: 0; }} }}
</style>
<defs><clipPath id="c"><rect width="{w}" height="{h}" rx="14"/></clipPath></defs>
<g clip-path="url(#c)">
  <rect width="{w}" height="{h}" fill="#0a0c10"/>
  <rect y="0" width="{w}" height="2" fill="{ACCENT}"/>
  <text x="{w / 2}" y="{h / 2 + 7}" text-anchor="middle" font-family="{MONO}" font-size="21" fill="#6e7681"><tspan fill="{ACCENT}">$</tspan> open to: <tspan fill="#e6edf3">agent infra</tspan> · <tspan fill="#e6edf3">eval tooling</tspan> · <tspan fill="#e6edf3">research collabs</tspan> · <tspan fill="#e6edf3">hard problems</tspan><tspan class="blink" fill="#e6edf3"> ▋</tspan></text>
</g>
<rect x=".5" y=".5" width="{w - 1}" height="{h - 1}" rx="14" fill="none" stroke="#21262d"/>
</svg>'''


if __name__ == "__main__":
    out = ROOT / "assets"
    (out / "banner.svg").write_text(banner())
    (out / "footer.svg").write_text(footer())
    print("wrote", out / "banner.svg", out / "footer.svg")
