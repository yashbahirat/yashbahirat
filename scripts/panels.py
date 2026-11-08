"""Generates the static README panels in assets/: boot.svg, agent.svg, procs.svg, tools.svg.

Usage: python scripts/panels.py   (run from repo root)
All panels share one window style (matches the contributions card) and embed subset fonts.
"""
import base64
import json
import pathlib
import re
import xml.dom.minidom
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


# ───────────────────────────── shared editorial bits ─────────────────────────────
from fontTools.ttLib import TTFont  # noqa: E402

SANS = "'SG',ui-sans-serif,system-ui,-apple-system,'Segoe UI',sans-serif"
_metrics = {}


def text_width(t, size, weight=500):
    if weight not in _metrics:
        f = TTFont(ASSETS / "fonts" / f"spacegrotesk-{weight}.woff2")
        _metrics[weight] = (f.getBestCmap(), f["hmtx"], f["head"].unitsPerEm)
    cmap, hmtx, upm = _metrics[weight]
    return sum(hmtx[cmap[ord(ch)]][0] if ord(ch) in cmap else upm * 0.55 for ch in t) * size / upm


def wrap(t, size, width, weight=500):
    lines, cur = [], ""
    for word in t.split():
        trial = f"{cur} {word}".strip()
        if text_width(trial, size, weight) <= width:
            cur = trial
        else:
            lines.append(cur)
            cur = word
    return lines + [cur]


def plain(w, h, label, body, extra_css="", aria=""):
    """Card without fake window chrome: small label top-left, content below."""
    return f'''<svg xmlns="http://www.w3.org/2000/svg" width="{w}" height="{h}" viewBox="0 0 {w} {h}" role="img" aria-label="{escape(aria or label)}">
<style>
  {font_face("SG", "spacegrotesk-500.woff2", 500)}
  {font_face("SG", "spacegrotesk-700.woff2", 700)}
  {font_face("JBM", "jbmono-500.woff2", 500)}
  .sans {{ font-family: {SANS}; }}
  .mono {{ font-family: {MONO}; }}
  .rise {{ animation: rise .7s cubic-bezier(.2,.8,.2,1) both; }}
  @keyframes rise {{ from {{ opacity: 0; transform: translateY(8px); }} to {{ opacity: 1; transform: none; }} }}
  {extra_css}
</style>
{body}
</svg>'''


def section_label(x, y, text, count=None):
    c = f'<tspan fill="{C["dim"]}">  {count}</tspan>' if count else ""
    return (f'<text class="mono" x="{x}" y="{y}" font-size="11" letter-spacing="2" fill="{C["muted"]}">'
            f'{escape(text.upper())}{c}</text>')


# ───────────────────────────── hero line under the banner ─────────────────────────────
def hero():
    Wh, H, BG = 1280, 124, "#05070d"
    words = [("agents.", C["blue"]), ("harnesses.", C["purple"]), ("inference.", C["green"])]
    slot = 2.6
    T = slot * len(words)
    css = []
    groups = []
    for i, (wd, col) in enumerate(words):
        a = 100 * i / len(words)
        b = 100 * (i * slot + 0.45) / T
        c = 100 * ((i + 1) * slot - 0.45) / T
        e = 100 * (i + 1) * slot / T
        pre = f"0%,{a - 0.01:.2f}%{{opacity:0;transform:translateY(28px)}}" if i else ""
        css.append(
            f"@keyframes w{i}{{{pre}{a:.2f}%{{opacity:0;transform:translateY(28px)}}"
            f"{b:.2f}%,{c:.2f}%{{opacity:1;transform:none}}"
            f"{e:.2f}%,100%{{opacity:0;transform:translateY(-28px)}}}}"
            f".w{i}{{animation:w{i} {T}s cubic-bezier(.6,0,.2,1) infinite}}")
        groups.append(f'<text class="sans w{i}" x="1232" y="94" text-anchor="end" font-size="29" font-weight="700" fill="{col}">{wd}</text>')
    body = f'''<defs>
  <clipPath id="frame"><rect width="{Wh}" height="{H}" rx="16"/></clipPath>
  <clipPath id="slot"><rect x="900" y="62" width="340" height="44"/></clipPath>
  <linearGradient id="trd" x1="0" x2="1"><stop offset="0" stop-color="{C["blue"]}"/><stop offset="1" stop-color="#d2a8ff"/></linearGradient>
  <linearGradient id="edge" x1="0" x2="1"><stop offset="0" stop-color="#58a6ff" stop-opacity="0"/><stop offset=".5" stop-color="#bc8cff"/><stop offset="1" stop-color="#58a6ff" stop-opacity="0"/></linearGradient>
</defs>
<g clip-path="url(#frame)">
  <rect width="{Wh}" height="{H}" fill="{BG}"/>
  <rect width="{Wh}" height="1.5" fill="url(#edge)"/>
  <text class="mono" x="50" y="46" font-size="15" letter-spacing="3" fill="{C["muted"]}">CURRENTLY</text>
  <text class="sans rise" x="48" y="94" font-size="29" font-weight="700" fill="#f0f6fc">Junior Agentic Coder <tspan font-weight="500" fill="{C["muted"]}">at</tspan> <tspan fill="url(#trd)">Tradeify</tspan></text>
  <text class="mono" x="1232" y="46" text-anchor="end" font-size="15" letter-spacing="3" fill="{C["muted"]}">BUILDING</text>
  <g clip-path="url(#slot)">{"".join(groups)}</g>
</g>
<rect x=".5" y=".5" width="{Wh - 1}" height="{H - 1}" rx="16" fill="none" stroke="#21262d"/>'''
    return plain(Wh, H, "Junior Agentic Coder at Tradeify", body, "".join(css),
                 aria="Junior Agentic Coder at Tradeify, building agents, harnesses and inference")


# ───────────────────────────── pull quote ─────────────────────────────
def quote():
    h = 128
    body = f'''<defs><linearGradient id="q" x1="0" x2="1"><stop offset="0" stop-color="#f0f6fc"/><stop offset=".55" stop-color="#a5d6ff"/><stop offset="1" stop-color="#d2a8ff"/></linearGradient></defs>
<rect x=".5" y=".5" width="{W - 1}" height="{h - 1}" rx="12" fill="{C["bg"]}" stroke="{C["border"]}"/>
<rect x="32" y="30" width="3" height="68" rx="1.5" fill="url(#q)"/>
<text class="sans rise" x="52" y="50" font-size="16" font-weight="500" fill="{C["muted"]}">The model is the engine. The harness is the car.</text>
<text class="sans rise" style="animation-delay:.25s" x="51" y="86" font-size="28" font-weight="700" fill="url(#q)">I build cars.</text>
<text class="mono" x="52" y="108" font-size="10" letter-spacing="2" fill="{C["dim"]}">ON HARNESS ENGINEERING</text>'''
    return plain(W, h, "quote", body, aria="The model is the engine. The harness is the car. I build cars.")


# ───────────────────────────── selected work ─────────────────────────────
STATUS = {"in progress": C["orange"], "shipped": C["green"], "hackathon": C["blue"]}


def project_card(x, y, w, h, idx, title, status, desc, tags, desc_w, delay_s, extra=""):
    col = STATUS[status]
    sw = len(status) * 6.6 + 26
    out = [f'<g class="rise" style="animation-delay:{delay_s:.2f}s">',
           f'<rect x="{x + .5}" y="{y + .5}" width="{w - 1}" height="{h - 1}" rx="12" fill="{C["bg"]}" stroke="{C["border"]}"/>',
           f'<text class="mono" x="{x + 24}" y="{y + 34}" font-size="11" letter-spacing="2" fill="{C["dim"]}">{idx}</text>',
           f'<rect x="{x + w - 24 - sw:.1f}" y="{y + 20}" width="{sw:.1f}" height="20" rx="10" fill="{col}" fill-opacity=".12" stroke="{col}" stroke-opacity=".4"/>',
           f'<circle cx="{x + w - 24 - sw + 11:.1f}" cy="{y + 30}" r="3" fill="{col}"/>',
           f'<text class="mono" x="{x + w - 24 - sw + 19:.1f}" y="{y + 34}" font-size="11" fill="{col}">{status}</text>',
           f'<text class="sans" x="{x + 24}" y="{y + 70}" font-size="22" font-weight="700" fill="#f0f6fc">{escape(title)}</text>']
    ly = y + 98
    for line in wrap(desc, 14, desc_w):
        out.append(f'<text class="sans" x="{x + 24}" y="{ly}" font-size="14" fill="#c9d1d9">{escape(line)}</text>')
        ly += 21
    tx = x + 24
    for t in tags:
        tw = len(t) * 6.6 + 16
        out.append(f'<rect x="{tx:.1f}" y="{y + h - 40}" width="{tw:.1f}" height="22" rx="6" fill="{C["bar"]}" stroke="{C["border"]}"/>'
                   f'<text class="mono" x="{tx + 8:.1f}" y="{y + h - 25}" font-size="11" fill="{C["muted"]}">{escape(t)}</text>')
        tx += tw + 8
    out.append(extra)
    out.append("</g>")
    return "".join(out)


def ledger_art(x, y):
    """Small chained-blocks motif for MPTL: each memory linked to the one before it."""
    out = []
    for i in range(4):
        bx, by = x + i * 62, y + (12 if i % 2 else 0)
        last = i == 3
        stroke = C["purple"] if last else C["border"]
        out.append(f'<rect x="{bx}" y="{by}" width="46" height="56" rx="8" fill="{C["bar"]}" stroke="{stroke}"/>')
        out.append(f'<rect x="{bx + 9}" y="{by + 12}" width="28" height="4" rx="2" fill="{C["dim"]}"/>')
        out.append(f'<rect x="{bx + 9}" y="{by + 22}" width="20" height="4" rx="2" fill="{C["dim"]}"/>')
        out.append(f'<circle cx="{bx + 23}" cy="{by + 42}" r="5" fill="{C["purple"] if last else C["blue"]}" fill-opacity="{1 if last else .55}"/>')
        if i:
            px, py = bx - 16, by + 28
            out.append(f'<line x1="{px}" y1="{py - (12 if i % 2 else -12)}" x2="{bx}" y2="{py}" stroke="{C["border"]}" stroke-width="1.5" stroke-dasharray="3 3" class="flow"/>')
    return "".join(out)


def projects():
    gap, top = 16, 36
    fh, hh = 204, 228
    half = (W - gap) / 2
    css = (".flow { animation: flow 1.6s linear infinite; } @keyframes flow { to { stroke-dashoffset: -12; } }")
    body = [section_label(2, 18, "selected work", "03")]
    body.append(project_card(
        0, top, W, fh, "01", "MPTL: Memory Provenance & Trust Ledger", "in progress",
        "A tamper-evident ledger for agent memory. Every memory an LLM agent writes is traced back to "
        "its source, so you can audit what it knows and decide what to trust.",
        ["LLM agents", "provenance", "Python", "Claude Code"], 460, 0.1,
        extra=ledger_art(530, top + 70)))
    y2 = top + fh + gap
    body.append(project_card(
        0, y2, half, hh, "02", "Sovereign Agentic Workbench", "hackathon",
        "Air-gapped agentic AI for refinery engineers: local GGUF models, local RAG, sandboxed code "
        "execution and P&ID vision. Team build for Smart India Hackathon.",
        ["local LLMs", "RAG", "sandboxing"], half - 48, 0.25))
    body.append(project_card(
        half + gap, y2, half, hh, "03", "RegulOS", "shipped",
        "Detects where GDPR, the EU AI Act and India's DPDP Act conflict for the same AI system, "
        "before it ships.",
        ["compliance", "GDPR", "EU AI Act", "DPDP"], half - 48, 0.4))
    h = y2 + hh + 2
    return plain(W, h, "selected work", "".join(body), css,
                 aria="Selected work: MPTL, Sovereign Agentic Workbench, RegulOS")


# ───────────────────────────── tools ─────────────────────────────
def tools():
    icons = json.loads((ASSETS / "icons.json").read_text())
    groups = [
        ("agents & LLMs", [("claude", "Claude Code"), ("anthropic", "Anthropic API"), ("openai", "OpenAI"),
                           ("modelcontextprotocol", "MCP"), ("langchain", "LangChain"), ("langgraph", "LangGraph"),
                           ("langsmith", "LangSmith"), ("langfuse", "Langfuse"), ("pydantic", "Pydantic"),
                           ("huggingface", "Hugging Face")]),
        ("inference", [("vllm", "vLLM"), ("ollama", "Ollama"), ("onnx", "ONNX"), ("nvidia", "CUDA")]),
        ("ML & data science", [("python", "Python"), ("pytorch", "PyTorch"), ("numpy", "NumPy"), ("pandas", "pandas"),
                               ("scikitlearn", "scikit-learn"), ("opencv", "OpenCV"), ("jupyter", "Jupyter"),
                               ("streamlit", "Streamlit")]),
        ("web & data", [("typescript", "TypeScript"), ("nodedotjs", "Node.js"), ("react", "React"), ("nextdotjs", "Next.js"),
                        ("tailwindcss", "Tailwind"), ("fastapi", "FastAPI"), ("postgresql", "Postgres"), ("mongodb", "MongoDB"),
                        ("supabase", "Supabase")]),
        ("infra", [("docker", "Docker"), ("linux", "Linux"), ("gnubash", "Bash"), ("git", "Git"),
                   ("githubactions", "GitHub Actions"), ("aws", "AWS"), ("googlecloud", "Google Cloud"),
                   ("cloudflare", "Cloudflare"), ("vercel", "Vercel")]),
    ]
    css = (".pop { animation: pop .55s cubic-bezier(.2,.9,.3,1.4) both; transform-box: fill-box; transform-origin: center; }"
           "@keyframes pop { from { opacity: 0; transform: scale(.7); } to { opacity: 1; transform: none; } }")
    out, defs = [section_label(2, 18, "toolkit")], []
    tile, gap, n = 66, 9.33, 0
    y = 36
    out.append(f'<rect x=".5" y="{y + .5}" width="{W - 1}" height="{{H}}" rx="12" fill="{C["bg"]}" stroke="{C["border"]}"/>')
    y += 34
    for gname, items in groups:
        out.append(f'<text class="sans" x="28" y="{y}" font-size="13" font-weight="500" fill="{C["muted"]}">{escape(gname[0].upper() + gname[1:])}</text>')
        ty = y + 14
        for j, (slug, label) in enumerate(items):
            if slug.startswith("@"):
                mono, hexv = slug[1:].split(":")
                ic = {"hex": hexv, "path": None, "mono": mono}
            else:
                ic = icons[slug]
            hx = "#" + ic["hex"]
            r, g, b = (int(ic["hex"][k:k + 2], 16) for k in (0, 2, 4))
            fill = C["text"] if (0.299 * r + 0.587 * g + 0.114 * b) < 70 else hx
            if ic.get("inner") and ic["hex"] == "FFFFFF":
                fill = C["text"]
            tx = 28 + j * (tile + gap)
            defs.append(f'<radialGradient id="g{n}" cx=".5" cy=".35" r=".7"><stop offset="0" stop-color="{fill}" stop-opacity=".22"/><stop offset="1" stop-color="{fill}" stop-opacity="0"/></radialGradient>')
            out.append(
                f'<g class="pop" style="animation-delay:{0.2 + n * 0.05:.2f}s">'
                f'<rect x="{tx:.1f}" y="{ty}" width="{tile}" height="{tile}" rx="12" fill="{C["bar"]}" stroke="{C["border"]}"/>'
                f'<rect x="{tx:.1f}" y="{ty}" width="{tile}" height="{tile}" rx="12" fill="url(#g{n})"/>'
                + (f'<svg x="{tx + 18:.1f}" y="{ty + 18}" width="30" height="30" viewBox="0 0 24 24" fill="{C["text"]}" color="{C["text"]}" fill-rule="evenodd">{ic["inner"]}</svg>' if ic.get("inner") else
                   f'<path transform="translate({tx + 18:.1f} {ty + 18}) scale(1.25)" fill="{fill}" d="{ic["path"]}"/>' if ic["path"] else
                   f'<text class="sans" x="{tx + tile / 2:.1f}" y="{ty + 42}" text-anchor="middle" font-size="{22 if len(ic['mono']) <= 3 else 17}" font-weight="700" fill="{fill}">{ic["mono"]}</text>') +
                f'<text class="sans" x="{tx + tile / 2:.1f}" y="{ty + tile + 18}" text-anchor="middle" font-size="{12 if len(label) <= 11 else 10.5}" fill="{C["muted"]}">{label}</text></g>'
            )
            n += 1
        y = ty + tile + 52
    h = y - 12
    body = f'<defs>{"".join(defs)}</defs>' + "\n".join(out).replace("{H}", str(h - 37))
    return plain(W, h, "toolkit", body, css, aria="Toolkit: " + ", ".join(l for _, it in groups for _, l in it))


def publish(name, svg):
    """Write assets/<name>.<hash>.svg and point README at it, so GitHub never serves a stale copy."""
    import hashlib
    xml.dom.minidom.parseString(svg)  # GitHub serves these as standalone images: must be valid XML
    digest = hashlib.sha1(svg.encode()).hexdigest()[:8]
    for old_file in list(ASSETS.glob(f"{name}.svg")) + list(ASSETS.glob(f"{name}.*.svg")):
        old_file.unlink()
    fname = f"{name}.{digest}.svg"
    (ASSETS / fname).write_text(svg)
    readme = ROOT / "README.md"
    text = readme.read_text()
    text = re.sub(rf"\./assets/{name}(\.[0-9a-f]{{8}})?\.svg", f"./assets/{fname}", text)
    readme.write_text(text)
    print("wrote", f"assets/{fname}")


if __name__ == "__main__":
    for name, fn in (("hero", hero), ("quote", quote), ("agent", agent), ("projects", projects), ("toolkit", tools)):
        publish(name, fn())
