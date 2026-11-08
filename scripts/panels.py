"""Generates the static README panels in assets/: boot.svg, agent.svg, procs.svg, tools.svg.

Usage: python scripts/panels.py   (run from repo root)
All panels share one window style (matches the contributions card) and embed subset fonts.
"""
import base64
import json
import pathlib
import re
from xml.sax.saxutils import escape

ROOT = pathlib.Path(__file__).resolve().parent.parent
ASSETS = ROOT / "assets"
W = 800
MONO = "'JBM',ui-monospace,Menlo,Consolas,monospace"

C = dict(bg="#0d1117", bar="#161b22", border="#30363d", text="#e6edf3", muted="#8b949e",
         dim="#484f58", blue="#58a6ff", purple="#bc8cff", green="#3fb950", red="#f85149",
         orange="#d29922", key="#7ee787", string="#a5d6ff", number="#79c0ff")


def font_face(family, file, weight):
    data = base64.b64encode((ASSETS / "fonts" / file).read_bytes()).decode()
    return (f"@font-face{{font-family:'{family}';font-weight:{weight};"
            f"src:url(data:font/woff2;base64,{data}) format('woff2');}}")


def window(h, title, body, extra_css=""):
    return f'''<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{h}" viewBox="0 0 {W} {h}" role="img" aria-label="{escape(title)}">
<style>
  {font_face("JBM", "jbmono-500.woff2", 500)}
  {font_face("JBM", "jbmono-800.woff2", 800)}
  text {{ font-family: {MONO}; }}
  .in {{ animation: in .5s ease-out both; }}
  .blink {{ animation: blink 1.05s steps(1) infinite; }}
  @keyframes in {{ from {{ opacity: 0; transform: translateX(-6px); }} to {{ opacity: 1; transform: none; }} }}
  @keyframes blink {{ 50% {{ opacity: 0; }} }}
  {extra_css}
</style>
<rect x=".5" y=".5" width="{W - 1}" height="{h - 1}" rx="10" fill="{C['bg']}" stroke="{C['border']}"/>
<path d="M.5 10.5a10 10 0 0 1 10-10h{W - 21}a10 10 0 0 1 10 10v20h-{W - 1}z" fill="{C['bar']}"/>
<line x1="0" y1="30.5" x2="{W}" y2="30.5" stroke="{C['border']}"/>
<circle cx="20" cy="15.5" r="5" fill="#ff5f57"/><circle cx="38" cy="15.5" r="5" fill="#febc2e"/><circle cx="56" cy="15.5" r="5" fill="#28c840"/>
<text x="{W / 2}" y="20" text-anchor="middle" fill="{C['muted']}" font-size="12">{escape(title)}</text>
{body}
</svg>'''


def delay(i, base=0.25, step=0.14):
    return f'style="animation-delay:{base + i * step:.2f}s"'


# ───────────────────────────── boot ─────────────────────────────
def boot():
    rows = [
        (True, "loading harness", "claude-code"),
        (True, "mounting tools", "mcp · bash · fs · browser"),
        (True, "spawning subagents", "4/4 healthy"),
        (True, "memory", "provenance-tracked"),
        (True, "evals", "green"),
        (False, "prompt engineering", "superseded by harness engineering"),
        (False, "sleep schedule", "not found"),
    ]
    cw, x_label, x_val = 13 * 0.6, 100, 380
    out = [f'<text x="28" y="60" font-size="13" fill="{C["muted"]}"><tspan fill="{C["green"]}">$</tspan> ./boot --verbose</text>']
    y = 92
    for i, (ok, label, val) in enumerate(rows):
        col = C["green"] if ok else C["red"]
        dots = "." * int((x_val - 12 - (x_label + len(label) * cw)) / cw)
        out.append(
            f'<g class="in" {delay(i)}>'
            f'<rect x="28" y="{y - 13}" width="56" height="18" rx="4" fill="{col}" fill-opacity=".15" stroke="{col}" stroke-opacity=".5"/>'
            f'<text x="56" y="{y}" text-anchor="middle" font-size="11" font-weight="800" fill="{col}">{"OK" if ok else "FAIL"}</text>'
            f'<text x="{x_label}" y="{y}" font-size="13" fill="{C["text"]}">{label} <tspan fill="{C["dim"]}">{dots}</tspan></text>'
            f'<text x="{x_val}" y="{y}" font-size="13" fill="{col if not ok else C["blue"]}">{escape(val)}</text></g>'
        )
        y += 26
    n = len(rows)
    out.append(f'<g class="in" {delay(n)}><text x="28" y="{y + 6}" font-size="13" fill="{C["muted"]}">ready. awaiting task<tspan class="blink" fill="{C["text"]}"> ▋</tspan></text></g>')
    qy = y + 52
    out.append(f'<line x1="28" y1="{qy - 26}" x2="{W - 28}" y2="{qy - 26}" stroke="{C["border"]}" stroke-dasharray="2 5"/>')
    out.append(
        f'<defs><linearGradient id="q" x1="0" x2="1"><stop offset="0" stop-color="{C["blue"]}"/><stop offset="1" stop-color="{C["purple"]}"/></linearGradient></defs>'
        f'<g class="in" {delay(n + 1)}><text x="28" y="{qy}" font-size="15" font-weight="800" fill="url(#q)">'
        f'The model is the engine. The harness is the car. I build cars.</text></g>'
    )
    return window(qy + 26, "yash@agentic: ~ — ./boot --verbose", "\n".join(out))


# ───────────────────────────── agent.yaml ─────────────────────────────
AGENT_YAML = '''agent:
  name: Yash Bahirat
  role: Junior Agentic Coder @ Tradeify
  mode: research-first, ship-fast
  harness: claude-code

  focus:
    - harness_engineering     # the loop around the model: context, tools, retries, recovery
    - agent_engineering       # planning, memory, subagents, long-horizon reliability
    - inference_engineering   # latency, cost, throughput, serving

  beliefs:
    - "if it isn't evaluated, it doesn't work"
    - "an agent that can't explain its memory can't be trusted"
    - "context is a budget, spend it like money"

  research:
    published: "Harmony-Bot — IJAECS, Vol. 12, Iss. 7 (2025)"
    patents: 1
    in_progress: 1

  hallucination_tolerance: 0'''


def yaml_tokens(line):
    """Tiny YAML highlighter -> list of (text, colour)."""
    m = re.match(r"^(\s*)(.*)$", line)
    indent, rest = m.groups()
    toks = [(indent, C["text"])]
    comment = ""
    if " #" in rest:
        rest, comment = rest.split(" #", 1)
        comment = " #" + comment
    if rest.startswith("- "):
        toks.append(("- ", C["muted"]))
        rest = rest[2:]
    km = re.match(r"^([A-Za-z_]+):(\s*)(.*)$", rest)
    if km:
        k, sp, v = km.groups()
        toks += [(k, C["key"]), (":", C["muted"]), (sp, C["text"])]
        rest = v
    if rest:
        trimmed = rest.rstrip()
        if trimmed.startswith('"'):
            col = C["string"]
        elif re.fullmatch(r"\d+", trimmed):
            col = C["number"]
        elif re.fullmatch(r"[a-z_]+", trimmed) and not km:
            col = C["text"]
        else:
            col = C["string"] if km else C["text"]
        toks.append((rest, col))
    if comment:
        toks.append((comment, C["muted"]))
    return toks


def agent():
    lines = AGENT_YAML.split("\n")
    lh, y0, x_code = 20, 58, 64
    out = []
    for i, line in enumerate(lines):
        y = y0 + i * lh
        spans = "".join(f'<tspan fill="{c}">{escape(t)}</tspan>' for t, c in yaml_tokens(line) if t)
        out.append(
            f'<g class="in" {delay(i, 0.15, 0.05)}>'
            f'<text x="44" y="{y}" text-anchor="end" font-size="12" fill="{C["dim"]}">{i + 1}</text>'
            f'<text x="{x_code}" y="{y}" font-size="12.5" xml:space="preserve">{spans}</text></g>'
        )
    body_end = y0 + len(lines) * lh
    h = body_end + 30
    sb = h - 24
    out.insert(0, f'<line x1="54.5" y1="31" x2="54.5" y2="{sb}" stroke="{C["border"]}"/>')
    out.append(
        f'<rect x=".5" y="{sb}" width="{W - 1}" height="23.5" fill="{C["bar"]}"/>'
        f'<path d="M.5 {sb}h{W - 1}" stroke="{C["border"]}"/>'
        f'<rect x="1" y="{sb + 0.5}" width="70" height="23" fill="{C["blue"]}" fill-opacity=".85"/>'
        f'<text x="36" y="{sb + 16}" text-anchor="middle" font-size="11" font-weight="800" fill="#0d1117">NORMAL</text>'
        f'<text x="84" y="{sb + 16}" font-size="11" fill="{C["muted"]}">agent.yaml</text>'
        f'<text x="{W - 16}" y="{sb + 16}" text-anchor="end" font-size="11" fill="{C["muted"]}">yaml · utf-8 · ln {len(lines)}, col 1 · <tspan fill="{C["green"]}">● 0 hallucinations</tspan></text>'
    )
    return window(h, "~/yash/agent.yaml", "\n".join(out))


# ───────────────────────────── ps / htop ─────────────────────────────
def procs():
    css = (".fill { animation: fill 1.2s cubic-bezier(.2,.8,.2,1) both; transform-box: fill-box; transform-origin: left; }"
           "@keyframes fill { from { transform: scaleX(0); } to { transform: none; } }"
           ".throb { animation: throb 2.2s ease-in-out infinite; }"
           "@keyframes throb { 50% { opacity: .55; } }")
    out = []

    def meter(y, label, pct, col, i):
        x0, w = 124, 270
        out.append(
            f'<text x="28" y="{y}" font-size="12" fill="{C["blue"]}" font-weight="800">{label}</text>'
            f'<text x="{x0 - 8}" y="{y}" font-size="12" fill="{C["muted"]}">[</text>'
            f'<rect x="{x0}" y="{y - 10}" width="{w}" height="12" rx="2" fill="{C["bar"]}"/>'
            f'<rect class="fill throb" style="animation-delay:{0.2 + i * 0.15:.2f}s,0s" x="{x0}" y="{y - 10}" width="{w * pct / 100:.0f}" height="12" rx="2" fill="{col}"/>'
            f'<text x="{x0 + w + 4}" y="{y}" font-size="12" fill="{C["muted"]}">] <tspan fill="{C["text"]}">{pct}%</tspan></text>'
        )

    meter(58, "focus", 94, C["green"], 0)
    meter(78, "curiosity", 100, C["purple"], 1)
    meter(98, "sleep", 12, C["red"], 2)
    out.append(
        f'<text x="470" y="58" font-size="12" fill="{C["muted"]}">Tasks: <tspan fill="{C["text"]}" font-weight="800">3</tspan>, <tspan fill="{C["green"]}" font-weight="800">2 running</tspan></text>'
        f'<text x="470" y="78" font-size="12" fill="{C["muted"]}">Load average: <tspan fill="{C["text"]}">always</tspan></text>'
        f'<text x="470" y="98" font-size="12" fill="{C["muted"]}">Uptime: <tspan fill="{C["text"]}">shipping</tspan></text>'
    )

    hy = 124
    out.append(f'<rect x="1" y="{hy - 14}" width="{W - 2}" height="20" fill="{C["green"]}"/>')
    for x, t in ((28, "PID"), (78, "S"), (108, "STATE"), (196, "COMMAND")):
        out.append(f'<text x="{x}" y="{hy}" font-size="12" font-weight="800" fill="#0d1117">{t}</text>')

    rows = [
        ("001", "R", "running", C["green"], "MPTL", "Memory Provenance & Trust Ledger · auditable memory for LLM agents"),
        ("002", "S", "exited 0", C["muted"], "RegulOS", "cross-jurisdictional AI-compliance conflict detection"),
        ("003", "R", "running", C["green"], "Sovereign Agentic Workbench", "air-gapped, on-prem agentic AI for industrial operations"),
    ]
    y = hy + 30
    for i, (pid, s, state, col, name, desc) in enumerate(rows):
        hl = i == 0
        if hl:
            out.append(f'<rect x="1" y="{y - 16}" width="{W - 2}" height="44" fill="{C["blue"]}" fill-opacity=".12"/>'
                       f'<rect x="1" y="{y - 16}" width="3" height="44" fill="{C["blue"]}"/>')
        dot = (f'<circle class="throb" cx="{110}" cy="{y - 4}" r="3.5" fill="{col}"/>' if s == "R"
               else f'<circle cx="110" cy="{y - 4}" r="3.5" fill="none" stroke="{col}"/>')
        out.append(
            f'<g class="in" {delay(i, 0.5, 0.15)}>'
            f'<text x="28" y="{y}" font-size="12.5" fill="{C["muted"]}">{pid}</text>'
            f'<text x="78" y="{y}" font-size="12.5" font-weight="800" fill="{col}">{s}</text>{dot}'
            f'<text x="120" y="{y}" font-size="12" fill="{col}">{state}</text>'
            f'<text x="196" y="{y}" font-size="13" font-weight="800" fill="{C["text"]}">{escape(name)}</text>'
            f'<text x="196" y="{y + 18}" font-size="11.5" fill="{C["muted"]}">{escape(desc)}</text></g>'
        )
        y += 50

    fy = y - 4
    keys = [("F1", "hire"), ("F2", "collab"), ("F3", "research"), ("F5", "ship"), ("F10", "quit (never)")]
    x = 28
    for k, label in keys:
        kw = len(k) * 7.8 + 8
        out.append(f'<rect x="{x}" y="{fy - 12}" width="{kw:.0f}" height="17" fill="{C["blue"]}"/>'
                   f'<text x="{x + 4}" y="{fy}" font-size="12" font-weight="800" fill="#0d1117">{k}</text>'
                   f'<text x="{x + kw + 4:.0f}" y="{fy}" font-size="12" fill="{C["text"]}">{label}</text>')
        x += kw + 12 + len(label) * 7.2 + 10
    return window(fy + 20, "htop — yash@agentic", "\n".join(out), css)


# ───────────────────────────── tools ─────────────────────────────
def tools():
    icons = json.loads((ASSETS / "icons.json").read_text())
    groups = [
        ("# agent stack", [("claude", "Claude Code"), ("modelcontextprotocol", "MCP"), ("langchain", "LangGraph"),
                           ("vllm", "vLLM"), ("ollama", "Ollama"), ("huggingface", "Hugging Face")]),
        ("# core", [("python", "Python"), ("pytorch", "PyTorch"), ("typescript", "TypeScript"), ("fastapi", "FastAPI"),
                    ("docker", "Docker"), ("linux", "Linux"), ("gnubash", "Bash"), ("cloudflare", "Cloudflare"),
                    ("postgresql", "Postgres"), ("git", "Git")]),
    ]
    css = (".pop { animation: pop .55s cubic-bezier(.2,.9,.3,1.4) both; transform-box: fill-box; transform-origin: center; }"
           "@keyframes pop { from { opacity: 0; transform: scale(.7); } to { opacity: 1; transform: none; } }")
    out = [f'<text x="28" y="60" font-size="13" fill="{C["muted"]}"><tspan fill="{C["green"]}">$</tspan> which --all tools</text>']
    tile, gap, y, n = 66, 9.33, 82, 0
    defs = []
    for gname, items in groups:
        out.append(f'<text x="28" y="{y}" font-size="12" fill="{C["dim"]}">{gname}</text>')
        ty = y + 12
        for j, (slug, label) in enumerate(items):
            ic = icons[slug]
            hx = "#" + ic["hex"]
            r, g, b = (int(ic["hex"][k:k + 2], 16) for k in (0, 2, 4))
            fill = C["text"] if (0.299 * r + 0.587 * g + 0.114 * b) < 70 else hx
            tx = 28 + j * (tile + gap)
            defs.append(f'<radialGradient id="g{n}" cx=".5" cy=".35" r=".7"><stop offset="0" stop-color="{fill}" stop-opacity=".22"/><stop offset="1" stop-color="{fill}" stop-opacity="0"/></radialGradient>')
            out.append(
                f'<g class="pop" style="animation-delay:{0.2 + n * 0.05:.2f}s">'
                f'<rect x="{tx:.1f}" y="{ty}" width="{tile}" height="{tile}" rx="12" fill="{C["bar"]}" stroke="{C["border"]}"/>'
                f'<rect x="{tx:.1f}" y="{ty}" width="{tile}" height="{tile}" rx="12" fill="url(#g{n})"/>'
                f'<path transform="translate({tx + 18:.1f} {ty + 18}) scale(1.25)" fill="{fill}" d="{ic["path"]}"/>'
                f'<text x="{tx + tile / 2:.1f}" y="{ty + tile + 17}" text-anchor="middle" font-size="11" fill="{C["muted"]}">{label}</text></g>'
            )
            n += 1
        y = ty + tile + 48
    body = f'<defs>{"".join(defs)}</defs>' + "\n".join(out)
    return window(y - 18, "~/yash — which --all tools", body, css)


if __name__ == "__main__":
    for name, fn in (("boot", boot), ("agent", agent), ("procs", procs), ("tools", tools)):
        (ASSETS / f"{name}.svg").write_text(fn())
        print("wrote", f"assets/{name}.svg")
