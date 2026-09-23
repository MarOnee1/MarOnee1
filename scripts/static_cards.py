"""Static cards (drawn once, committed to assets/)."""
import json
import os

from cards import (ACCENTS, BG_BOTTOM, BG_TOP, BLOOD, CORAL, CRIMSON, DIM, INK,
                   LINE, MUTED, RED, ROSE, card_frame, delay, font, svg, text)

W = 900
HERE = os.path.dirname(os.path.abspath(__file__))


# ── 3D wordmark ─────────────────────────────────────────────────────────
def wordmark(label="MARONEE1"):
    h = 190
    size, sp = 100, 4
    f = font("bold")
    w = f.width(label, size, sp)
    x, base = (W - w) / 2, 128
    d = f.path(label, size, x, base, sp)
    depth = 9
    shades = ["#1c0a0d", "#240c10", "#2d0e13", "#370f16", "#421119", "#4d131c", "#58151f", "#631722", "#6e1925"]
    defs = f"""
  <linearGradient id="face" x1="0" y1="0" x2="0" y2="1">
    <stop offset="0" stop-color="#fff1f1"/><stop offset=".55" stop-color="#fca5a5"/><stop offset="1" stop-color="{RED}"/>
  </linearGradient>
  <linearGradient id="shine" x1="0" y1="0" x2="1" y2="0">
    <stop offset="0" stop-color="#fff" stop-opacity="0"/><stop offset=".5" stop-color="#fff" stop-opacity=".75"/><stop offset="1" stop-color="#fff" stop-opacity="0"/>
  </linearGradient>
  <filter id="glow" x="-10%" y="-40%" width="120%" height="180%"><feGaussianBlur stdDeviation="14"/></filter>
  <mask id="txt"><path d="{d}" fill="#fff"/></mask>"""
    body = f'<path d="{d}" fill="{RED}" opacity=".35" filter="url(#glow)"/>'
    body += '<g class="k-in">'
    for k in range(depth, 0, -1):
        body += f'<path d="{d}" fill="{shades[k-1]}" transform="translate({k*1.1:.1f} {k*1.3:.1f})"/>'
    body += f'<path d="{d}" fill="url(#face)"/>'
    body += "</g>"
    body += (f'<g mask="url(#txt)"><rect class="shine" x="{x-160:.0f}" y="0" width="140" height="{h}" '
             f'fill="url(#shine)" transform="skewX(-18)"/></g>')
    css = f"""
  .shine {{ animation: sweep 7s cubic-bezier(.4,0,.2,1) 1.2s infinite; }}
  @keyframes sweep {{ 0% {{ transform: skewX(-18deg) translateX(0); }} 35%,100% {{ transform: skewX(-18deg) translateX({w+420:.0f}px); }} }}
  @media (prefers-reduced-motion: reduce) {{ .shine {{ animation: none; opacity: 0; }} }}"""
    return svg(W, h, label, defs, body, css)


# ── ASCII wordmark in a terminal window ─────────────────────────────────
ASCII_NAME = [
    "███╗   ███╗ █████╗ ██████╗  ██████╗ ███╗   ██╗███████╗███████╗ ██╗",
    "████╗ ████║██╔══██╗██╔══██╗██╔═══██╗████╗  ██║██╔════╝██╔════╝███║",
    "██╔████╔██║███████║██████╔╝██║   ██║██╔██╗ ██║█████╗  █████╗  ╚██║",
    "██║╚██╔╝██║██╔══██║██╔══██╗██║   ██║██║╚██╗██║██╔══╝  ██╔══╝   ██║",
    "██║ ╚═╝ ██║██║  ██║██║  ██║╚██████╔╝██║ ╚████║███████╗███████╗ ██║",
    "╚═╝     ╚═╝╚═╝  ╚═╝╚═╝  ╚═╝ ╚═════╝ ╚═╝  ╚═══╝╚══════╝╚══════╝ ╚═╝",
]


def _box(ch, x, y, w, h):
    """Draw one box-drawing character as two thin parallel lines."""
    cx, cy, d = x + w / 2, y + h / 2, w * 0.2
    segs = {
        "═": [[(x, cy - d), (x + w, cy - d)], [(x, cy + d), (x + w, cy + d)]],
        "║": [[(cx - d, y), (cx - d, y + h)], [(cx + d, y), (cx + d, y + h)]],
        "╗": [[(x, cy - d), (cx + d, cy - d), (cx + d, y + h)], [(x, cy + d), (cx - d, cy + d), (cx - d, y + h)]],
        "╔": [[(x + w, cy - d), (cx - d, cy - d), (cx - d, y + h)], [(x + w, cy + d), (cx + d, cy + d), (cx + d, y + h)]],
        "╝": [[(x, cy + d), (cx + d, cy + d), (cx + d, y)], [(x, cy - d), (cx - d, cy - d), (cx - d, y)]],
        "╚": [[(x + w, cy + d), (cx - d, cy + d), (cx - d, y)], [(x + w, cy - d), (cx + d, cy - d), (cx + d, y)]],
    }[ch]
    return "".join("M" + " L".join(f"{px:.1f},{py:.1f}" for px, py in seg) for seg in segs)


def ascii_wordmark():
    cols = max(len(l) for l in ASCII_NAME)
    cw, chh = 12, 22
    art_w = cols * cw
    bar = 44
    ox = (W - art_w) / 2
    prompt_y = bar + 36
    oy = prompt_y + 24
    h = int(oy + len(ASCII_NAME) * chh + 58)
    defs, body = card_frame(W, h, rx=16)
    defs += f"""
  <linearGradient id="blk" x1="0" y1="{oy}" x2="0" y2="{oy + len(ASCII_NAME)*chh}" gradientUnits="userSpaceOnUse">
    <stop offset="0" stop-color="#ffe4e4"/><stop offset=".45" stop-color="{CORAL}"/><stop offset="1" stop-color="{CRIMSON}"/>
  </linearGradient>
  <filter id="bloom" x="-5%" y="-20%" width="110%" height="140%"><feGaussianBlur stdDeviation="7"/></filter>
  <clipPath id="type"><rect x="{ox-4:.1f}" y="{oy-4}" width="{art_w+8}" height="{len(ASCII_NAME)*chh+8}">
    <animate attributeName="width" values="0;0;{art_w+8}" keyTimes="0;.25;1" dur="1.9s" fill="freeze"/>
  </rect></clipPath>"""
    body += f'<rect x="1.5" y="1.5" width="{W-3}" height="{bar}" rx="15" fill="#ffffff" fill-opacity=".03"/>'
    body += f'<line x1="1" y1="{bar+1}" x2="{W-1}" y2="{bar+1}" stroke="{LINE}"/>'
    for i, c in enumerate([RED, CORAL, "#7f1d1d"]):
        body += f'<circle cx="{24 + i*20}" cy="{bar/2+1}" r="6" fill="{c}"/>'
    body += text("maronee1@github: ~ — zsh", 12, W / 2, bar / 2 + 5, DIM, "mono", anchor="middle")
    body += text("$", 13, ox, prompt_y, RED, "mono")
    body += text("figlet -f ansi-shadow maronee1", 13, ox + 18, prompt_y, MUTED, "mono")
    blocks, lines = "", ""
    for r, row in enumerate(ASCII_NAME):
        run = None
        for c, ch in enumerate(row + " "):
            x, y = ox + c * cw, oy + r * chh
            if ch == "█":
                run = c if run is None else run
                continue
            if run is not None:
                blocks += f'<rect x="{ox + run*cw:.1f}" y="{y:.1f}" width="{(c-run)*cw + .4:.1f}" height="{chh + .4:.1f}"/>'
                run = None
            if ch in "═║╗╔╝╚":
                lines += _box(ch, x, y, cw, chh)
    body += f'<g clip-path="url(#type)">'
    body += f'<g fill="{RED}" opacity=".45" filter="url(#bloom)">{blocks}</g>'
    body += f'<path d="{lines}" fill="none" stroke="#9f1239" stroke-width="1.6" stroke-linejoin="round"/>'
    body += f'<g fill="url(#blk)">{blocks}</g>'
    body += "</g>"
    cy = oy + len(ASCII_NAME) * chh + 34
    body += text("$", 13, ox, cy, RED, "mono")
    body += f'<rect class="k-blink" x="{ox+18:.1f}" y="{cy-12}" width="8" height="15" fill="{CORAL}"/>'
    return svg(W, h, "MARONEE1", defs, body)


# ── Portrait inside a terminal window ───────────────────────────────────
def portrait():
    dots = json.load(open(os.path.join(HERE, "_dots.json")))
    pitch_in, pitch_out = 8, 9
    xs = [float(x) for _, x, _ in dots]
    ys = [float(y) for *_, y in dots]
    minx, miny = min(xs), min(ys)
    gw = (max(xs) - minx) / pitch_in * pitch_out
    gh = (max(ys) - miny) / pitch_in * pitch_out
    bar = 44
    h = int(bar + gh + 60)
    ox, oy = (W - gw) / 2, bar + 30
    defs, body = card_frame(W, h, rx=16, aura=True)
    body += f'<rect x="1.5" y="1.5" width="{W-3}" height="{bar}" rx="15" fill="#ffffff" fill-opacity=".03"/>'
    body += f'<line x1="1" y1="{bar+1}" x2="{W-1}" y2="{bar+1}" stroke="{LINE}"/>'
    for i, c in enumerate([RED, CORAL, "#7f1d1d"]):
        body += f'<circle cx="{24 + i*20}" cy="{bar/2+1}" r="6" fill="{c}"/>'
    body += text("maronee1@github: ~/portrait", 12, W / 2, bar / 2 + 5, DIM, "mono", anchor="middle")
    colors = {"d1": "#5b1a20", "d2": "#8f1d24", "d3": CORAL, "d4": "#ffe4e4"}
    radii = {"d1": 1.8, "d2": 2.0, "d3": 2.3, "d4": 2.6}
    rows = {}
    for cls, x, y in dots:
        gx = ox + (float(x) - minx) / pitch_in * pitch_out
        gy = oy + (float(y) - miny) / pitch_in * pitch_out
        rows.setdefault(round(gy), []).append(f'<circle cx="{gx:.1f}" cy="{gy:.1f}" r="{radii[cls]}" fill="{colors[cls]}"/>')
    for k, y in enumerate(sorted(rows)):
        body += f'<g class="k-in"{delay(0.2 + k*0.03)}>' + "".join(rows[y]) + "</g>"
    # blinking prompt
    body += text("$", 13, 28, h - 22, RED, "mono")
    body += f'<rect class="k-blink" x="44" y="{h-34}" width="8" height="15" fill="{CORAL}"/>'
    return svg(W, h, "maronee1 dot portrait", defs, body)


# ── Divider ─────────────────────────────────────────────────────────────
def divider():
    h = 30
    defs = f"""
  <linearGradient id="l" x1="0" y1="0" x2="1" y2="0">
    <stop offset="0" stop-color="{RED}" stop-opacity="0"/><stop offset=".5" stop-color="{RED}" stop-opacity=".8"/><stop offset="1" stop-color="{RED}" stop-opacity="0"/>
  </linearGradient>
  <filter id="g" x="-100%" y="-100%" width="300%" height="300%"><feGaussianBlur stdDeviation="4"/></filter>"""
    c = W / 2
    body = f'<rect x="0" y="{h/2-.5}" width="{W}" height="1" fill="url(#l)"/>'
    body += f'<rect class="k-pulse" x="{c-6}" y="{h/2-6}" width="12" height="12" transform="rotate(45 {c} {h/2})" fill="{RED}" filter="url(#g)"/>'
    body += f'<rect x="{c-4.5}" y="{h/2-4.5}" width="9" height="9" transform="rotate(45 {c} {h/2})" fill="{CORAL}"/>'
    return svg(W, h, "divider", defs, body)


# ── Focus areas ─────────────────────────────────────────────────────────
ICONS = [
    '<polyline points="8,6 2,12 8,18"/><polyline points="16,6 22,12 16,18"/><line x1="14" y1="4" x2="10" y2="20"/>',
    '<ellipse cx="12" cy="5" rx="8" ry="3"/><path d="M4 5v14a8 3 0 0 0 16 0V5"/><path d="M4 12a8 3 0 0 0 16 0"/>',
    '<rect x="6" y="6" width="12" height="12" rx="2"/><rect x="9.5" y="9.5" width="5" height="5" rx="1"/>'
    '<path d="M9 2v4M15 2v4M9 18v4M15 18v4M2 9h4M2 15h4M18 9h4M18 15h4"/>',
    '<path d="M3 21h18"/><rect x="5" y="12" width="3" height="9" rx=".5"/><rect x="10.5" y="7" width="3" height="14" rx=".5"/>'
    '<rect x="16" y="3" width="3" height="18" rx=".5"/>',
]


def focus():
    items = [("Software Design", "Requirements · E-R · DFD", "ENGINEERING"),
             ("Databases", "Oracle SQL · Modeling", "DATA"),
             ("Low-Level Systems", "C · MIPS Assembly", "HARDWARE"),
             ("Data Analysis", "R · Statistics", "ANALYTICS")]
    gap, h = 16, 176
    cw = (W - 3 * gap) / 4
    defs = f"""
  <linearGradient id="bg" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="{BG_TOP}"/><stop offset="1" stop-color="{BG_BOTTOM}"/></linearGradient>
  <radialGradient id="au"><stop offset="0" stop-color="{RED}" stop-opacity=".22"/><stop offset="1" stop-color="{RED}" stop-opacity="0"/></radialGradient>
  <filter id="soft" x="-20%" y="-20%" width="140%" height="140%"><feGaussianBlur stdDeviation="5"/></filter>"""
    for i, acc in enumerate(ACCENTS):
        defs += (f'<linearGradient id="e{i}" x1="0" y1="0" x2="1" y2="1"><stop offset="0" stop-color="{acc}" stop-opacity=".85"/>'
                 f'<stop offset="1" stop-color="{BLOOD}" stop-opacity=".3"/></linearGradient>'
                 f'<clipPath id="c{i}"><rect x="{i*(cw+gap)+1:.1f}" y="1" width="{cw-2:.1f}" height="{h-2}" rx="16"/></clipPath>')
    body = ""
    for i, (title, sub, tag) in enumerate(items):
        x = i * (cw + gap)
        acc = ACCENTS[i]
        g = f'<g class="k-rise"{delay(i * .1)}>'
        g += f'<rect x="{x+1:.1f}" y="1" width="{cw-2:.1f}" height="{h-2}" rx="16" fill="url(#bg)"/>'
        g += f'<g clip-path="url(#c{i})"><ellipse cx="{x+cw*0.85:.1f}" cy="0" rx="{cw*0.7:.1f}" ry="{h*0.7:.1f}" fill="url(#au)"/></g>'
        g += f'<rect x="{x+1:.1f}" y="1" width="{cw-2:.1f}" height="{h-2}" rx="16" fill="none" stroke="{acc}" stroke-opacity=".3" stroke-width="3" filter="url(#soft)"/>'
        g += f'<rect x="{x+1:.1f}" y="1" width="{cw-2:.1f}" height="{h-2}" rx="16" fill="none" stroke="url(#e{i})" stroke-width="1.2"/>'
        g += (f'<g fill="none" stroke="{acc}" stroke-width="1.7" stroke-linecap="round" stroke-linejoin="round" '
              f'transform="translate({x+20:.1f} 26)">{ICONS[i]}</g>')
        g += text(font("bold").fit(title, 16, cw - 40), 16, x + 20, 92, INK, "bold")
        g += text(font("medium").fit(sub, 12.5, cw - 40), 12.5, x + 20, 116, MUTED, "medium")
        g += f'<line x1="{x+20:.1f}" y1="134" x2="{x+cw-20:.1f}" y2="134" stroke="#ffffff" stroke-opacity=".06"/>'
        g += text(tag, 10, x + 20, 156, acc, "mono", spacing=1.6)
        g += "</g>"
        body += g
    return svg(W, h, "Focus areas: " + ", ".join(t for t, _, _ in items), defs, body)


# ── Tech stack ──────────────────────────────────────────────────────────
def stack():
    items = [("C", "C", "Language"), ("SQL", "Oracle SQL", "Database"), ("ASM", "MIPS", "Low-level"),
             ("R", "R", "Analysis"), ("GIT", "Git", "Versioning"), ("GH", "GitHub", "Platform")]
    pad, gap = 32, 12
    h = 200
    cw = (W - 2 * pad - 5 * gap) / 6
    defs, body = card_frame(W, h)
    defs += f"""
  <linearGradient id="tile" x1="0" y1="0" x2="1" y2="1"><stop offset="0" stop-color="{CORAL}"/><stop offset="1" stop-color="{BLOOD}"/></linearGradient>
  <linearGradient id="sweep" x1="0" y1="0" x2="1" y2="0">
    <stop offset="0" stop-color="#fff" stop-opacity="0"/><stop offset=".5" stop-color="#fff" stop-opacity=".07"/><stop offset="1" stop-color="#fff" stop-opacity="0"/>
  </linearGradient>"""
    body += text("TECH.STACK", 13, pad, 48, RED, "mono", spacing=1.6)
    body += text("~/skills --list", 13, pad + font("mono").width("TECH.STACK", 13, 1.6) + 18, 48, DIM, "mono")
    body += f'<line x1="{pad}" y1="64" x2="{W-pad}" y2="64" stroke="{LINE}"/>'
    y = 84
    for i, (mono, name, kind) in enumerate(items):
        x = pad + i * (cw + gap)
        g = f'<g class="k-rise"{delay(.1 + i * .08)}>'
        g += (f'<rect x="{x:.1f}" y="{y}" width="{cw:.1f}" height="92" rx="14" fill="#ffffff" fill-opacity=".025" '
              f'stroke="#ffffff" stroke-opacity=".08"/>')
        g += f'<rect x="{x+14:.1f}" y="{y+14}" width="34" height="34" rx="9" fill="url(#tile)"/>'
        ms = 15 if len(mono) <= 1 else 12 if len(mono) == 2 else 10.5
        g += text(mono, ms, x + 31, y + 31 + ms * 0.36, "#fff", "bold", anchor="middle")
        g += text(name, 14, x + 14, y + 66, INK, "bold")
        g += text(kind, 11, x + 14, y + 82, DIM, "mono")
        g += "</g>"
        body += g
    body += f'<g clip-path="url(#clip)"><rect class="sw" x="-300" y="0" width="260" height="{h}" fill="url(#sweep)"/></g>'
    css = """
  .sw { animation: sw 6s ease-in-out 1.5s infinite; }
  @keyframes sw { 0% { transform: translateX(0); } 45%,100% { transform: translateX(1500px); } }
  @media (prefers-reduced-motion: reduce) { .sw { animation: none; } }"""
    return svg(W, h, "Tech stack: C, Oracle SQL, MIPS Assembly, R, Git, GitHub", defs, body, css)


if __name__ == "__main__":
    out = os.path.join(HERE, "..", "assets")
    for name, fn in [("wordmark.svg", ascii_wordmark), ("portrait.svg", portrait), ("divider.svg", divider),
                     ("focus.svg", focus), ("stack.svg", stack)]:
        with open(os.path.join(out, name), "w", encoding="utf-8") as f:
            f.write(fn())
        print("wrote", name)
