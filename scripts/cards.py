"""Design system for maronee1's profile cards.

Every piece of text is converted to vector outlines with fontTools, so the
cards look identical on every OS and browser (SVGs shown through <img> can't
load web fonts). Only the Python standard library + fontTools are needed.
"""
import math
import os
from xml.sax.saxutils import escape

from fontTools.pens.svgPathPen import SVGPathPen
from fontTools.pens.transformPen import TransformPen
from fontTools.ttLib import TTFont

HERE = os.path.dirname(os.path.abspath(__file__))
FONT_DIR = os.path.join(HERE, "..", "assets", "fonts")

# ── Palette ──────────────────────────────────────────────────────────────
BG_TOP = "#1a0d10"
BG_BOTTOM = "#0e0809"
INK = "#fafafa"
MUTED = "#b3a5a7"
DIM = "#6f6264"
LINE = "#3a1c21"
RED = "#ef4444"       # primary
CRIMSON = "#dc2626"
ROSE = "#fb7185"
CORAL = "#f87171"
BLOOD = "#991b1b"
ACCENTS = [RED, CORAL, ROSE, CRIMSON]
HEAT = ["#1f1315", "#4c1d1f", "#7f1d1d", "#dc2626", "#f87171"]  # 0 → max


# ── Text → outlines ──────────────────────────────────────────────────────
class Font:
    def __init__(self, filename):
        self.tt = TTFont(os.path.join(FONT_DIR, filename))
        self.glyphs = self.tt.getGlyphSet()
        self.cmap = self.tt.getBestCmap()
        self.upm = self.tt["head"].unitsPerEm
        self.fallback = self.cmap.get(ord("?"))

    def _glyph(self, ch):
        return self.cmap.get(ord(ch), self.fallback)

    def width(self, text, size, spacing=0.0):
        s = size / self.upm
        w = sum(self.glyphs[self._glyph(c)].width * s + spacing for c in text)
        return max(0.0, w - spacing) if text else 0.0

    def path(self, text, size, x, y, spacing=0.0, anchor="start"):
        w = self.width(text, size, spacing)
        if anchor == "middle":
            x -= w / 2
        elif anchor == "end":
            x -= w
        s = size / self.upm
        pen = SVGPathPen(self.glyphs)
        cx = 0.0
        for ch in text:
            g = self._glyph(ch)
            if ch != " ":
                self.glyphs[g].draw(TransformPen(pen, (s, 0, 0, -s, x + cx, y)))
            cx += self.glyphs[g].width * s + spacing
        return pen.getCommands()

    def fit(self, text, size, max_w, spacing=0.0):
        """Shorten text with an ellipsis so it never exceeds max_w."""
        text = " ".join((text or "").split())
        if self.width(text, size, spacing) <= max_w:
            return text
        while text and self.width(text + "…", size, spacing) > max_w:
            text = text[:-1]
        return text.rstrip(" ·,-") + "…"

    def wrap(self, text, size, max_w, max_lines):
        words = " ".join((text or "").split()).split(" ")
        lines, cur = [], ""
        for word in words:
            trial = (cur + " " + word).strip()
            if self.width(trial, size) <= max_w or not cur:
                cur = trial
            else:
                lines.append(cur)
                cur = word
        if cur:
            lines.append(cur)
        if len(lines) > max_lines:
            lines = lines[:max_lines]
            lines[-1] = self.fit(lines[-1] + " …", size, max_w)
        return [self.fit(l, size, max_w) for l in lines]


_fonts = {}


def font(name):
    files = {
        "bold": "SpaceGrotesk-Bold.woff",
        "medium": "SpaceGrotesk-Medium.woff",
        "mono": "JetBrainsMono-Medium.woff",
    }
    if name not in _fonts:
        _fonts[name] = Font(files[name])
    return _fonts[name]


def text(content, size, x, y, fill=INK, weight="medium", spacing=0.0,
         anchor="start", cls="", opacity=None):
    if not content:
        return ""
    d = font(weight).path(content, size, x, y, spacing, anchor)
    attrs = f' class="{cls}"' if cls else ""
    if opacity is not None:
        attrs += f' fill-opacity="{opacity}"'
    return f'<path{attrs} fill="{fill}" d="{d}"><title>{escape(content)}</title></path>'


# ── Shared building blocks ──────────────────────────────────────────────
BASE_CSS = """
  .k-in   { opacity: 0; animation: k-fade .7s cubic-bezier(.2,.7,.2,1) forwards; }
  .k-rise { opacity: 0; animation: k-rise .8s cubic-bezier(.2,.7,.2,1) forwards; }
  .k-grow { transform-box: fill-box; transform-origin: left center; transform: scaleX(0);
            animation: k-grow 1.2s cubic-bezier(.2,.7,.2,1) forwards; }
  .k-drift-a { animation: k-drift-a 14s ease-in-out infinite alternate; }
  .k-drift-b { animation: k-drift-b 18s ease-in-out infinite alternate; }
  .k-pulse { animation: k-pulse 2.4s ease-in-out infinite; }
  .k-blink { animation: k-blink 1.1s steps(1) infinite; }
  .k-spin  { transform-box: fill-box; transform-origin: center; animation: k-spin 14s linear infinite; }
  @keyframes k-fade  { to { opacity: 1; } }
  @keyframes k-rise  { from { opacity: 0; transform: translateY(6px); } to { opacity: 1; transform: translateY(0); } }
  @keyframes k-grow  { to { transform: scaleX(1); } }
  @keyframes k-drift-a { to { transform: translate(-40px, 18px); } }
  @keyframes k-drift-b { to { transform: translate(46px, -14px); } }
  @keyframes k-pulse { 0%,100% { opacity: 1; } 50% { opacity: .35; } }
  @keyframes k-blink { 50% { opacity: 0; } }
  @keyframes k-spin  { to { transform: rotate(360deg); } }
  @media (prefers-reduced-motion: reduce) {
    .k-in, .k-rise { opacity: 1; animation: none; }
    .k-grow { transform: none; animation: none; }
    .k-drift-a, .k-drift-b, .k-pulse, .k-spin, .k-blink { animation: none; }
  }
"""


def delay(seconds):
    return f' style="animation-delay:{seconds:.2f}s"'


def card_frame(w, h, rx=20, aura=True, glow=True):
    """Defs + background for a glassy dark-red card with a soft aura."""
    defs = f"""
  <linearGradient id="bg" x1="0" y1="0" x2="0" y2="1">
    <stop offset="0" stop-color="{BG_TOP}"/><stop offset="1" stop-color="{BG_BOTTOM}"/>
  </linearGradient>
  <linearGradient id="edge" x1="0" y1="0" x2="1" y2="1">
    <stop offset="0" stop-color="{RED}" stop-opacity=".75"/>
    <stop offset=".45" stop-color="{BLOOD}" stop-opacity=".35"/>
    <stop offset="1" stop-color="{ROSE}" stop-opacity=".6"/>
  </linearGradient>
  <radialGradient id="aura1"><stop offset="0" stop-color="{RED}" stop-opacity=".28"/><stop offset="1" stop-color="{RED}" stop-opacity="0"/></radialGradient>
  <radialGradient id="aura2"><stop offset="0" stop-color="{ROSE}" stop-opacity=".16"/><stop offset="1" stop-color="{ROSE}" stop-opacity="0"/></radialGradient>
  <filter id="soft" x="-20%" y="-20%" width="140%" height="140%"><feGaussianBlur stdDeviation="6"/></filter>
  <clipPath id="clip"><rect x="1" y="1" width="{w-2}" height="{h-2}" rx="{rx}"/></clipPath>"""
    body = f'<rect x="1" y="1" width="{w-2}" height="{h-2}" rx="{rx}" fill="url(#bg)"/>'
    if aura:
        body += (
            f'<g clip-path="url(#clip)">'
            f'<ellipse class="k-drift-a" cx="{w*0.82:.0f}" cy="{h*0.05:.0f}" rx="{w*0.32:.0f}" ry="{h*0.9:.0f}" fill="url(#aura1)"/>'
            f'<ellipse class="k-drift-b" cx="{w*0.12:.0f}" cy="{h*1.0:.0f}" rx="{w*0.28:.0f}" ry="{h*0.8:.0f}" fill="url(#aura2)"/>'
            f"</g>"
        )
    if glow:
        body += f'<rect x="1" y="1" width="{w-2}" height="{h-2}" rx="{rx}" fill="none" stroke="{RED}" stroke-opacity=".35" stroke-width="3" filter="url(#soft)"/>'
    body += f'<rect x="1" y="1" width="{w-2}" height="{h-2}" rx="{rx}" fill="none" stroke="url(#edge)" stroke-width="1.2"/>'
    return defs, body


def svg(w, h, label, defs, body, extra_css=""):
    return (
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{w}" height="{h}" viewBox="0 0 {w} {h}" '
        f'role="img" aria-label="{escape(label)}">\n'
        f"<defs>{defs}\n</defs>\n<style>{BASE_CSS}{extra_css}</style>\n{body}\n</svg>\n"
    )


def star_path(cx, cy, r_out, r_in):
    pts = []
    for i in range(10):
        r = r_out if i % 2 == 0 else r_in
        a = -math.pi / 2 + i * math.pi / 5
        pts.append(f"{cx + r*math.cos(a):.2f},{cy + r*math.sin(a):.2f}")
    return "M" + " L".join(pts) + " Z"


def pill(label, x, y, h=30, color=RED, size=13):
    w = font("medium").width(label, size) + 28
    return (
        f'<rect x="{x}" y="{y}" width="{w:.1f}" height="{h}" rx="{h/2}" fill="{color}" fill-opacity=".10" '
        f'stroke="{color}" stroke-opacity=".55"/>'
        + text(label, size, x + w / 2, y + h / 2 + size * 0.35, INK, "medium", anchor="middle")
    ), w
