"""Live cards: they are redrawn from real GitHub data by the workflow."""
import datetime as dt
import math

from cards import (ACCENTS, BLOOD, CORAL, CRIMSON, DIM, HEAT, INK, LINE, MUTED,
                   RED, ROSE, card_frame, delay, font, pill, star_path, svg, text)

W = 900


# ── 1. Hero / profile card ──────────────────────────────────────────────
def hero(user, avatar_data_uri):
    h = 250
    defs, body = card_frame(W, h)
    defs += f"""
  <linearGradient id="ring" x1="0" y1="0" x2="1" y2="1">
    <stop offset="0" stop-color="{CORAL}"/><stop offset=".5" stop-color="{CRIMSON}"/><stop offset="1" stop-color="{ROSE}"/>
  </linearGradient>
  <clipPath id="avatar"><circle cx="140" cy="125" r="66"/></clipPath>
  <filter id="halo" x="-50%" y="-50%" width="200%" height="200%"><feGaussianBlur stdDeviation="12"/></filter>"""
    login = user.get("login", "maronee1")
    name = user.get("name") or login
    bio = user.get("bio") or "Computer Engineering Student · UCAM"
    location = user.get("location") or "Murcia, Spain"

    body += f'<circle cx="140" cy="125" r="72" fill="{RED}" fill-opacity=".35" filter="url(#halo)"/>'
    if avatar_data_uri:
        body += (f'<circle cx="140" cy="125" r="66" fill="#140a0c"/>'
                 f'<image href="{avatar_data_uri}" x="74" y="59" width="132" height="132" '
                 f'preserveAspectRatio="xMidYMid slice" clip-path="url(#avatar)"/>')
    else:
        body += f'<circle cx="140" cy="125" r="66" fill="#241114"/>'
        body += text(name[:1].upper(), 56, 140, 145, CORAL, "bold", anchor="middle")
    body += f'<circle cx="140" cy="125" r="72" fill="none" stroke="url(#ring)" stroke-width="2.5"/>'
    # slow orbiting arc around the photo
    body += (f'<g class="k-spin"><circle cx="140" cy="125" r="82" fill="none" stroke="{RED}" '
             f'stroke-opacity=".7" stroke-width="1.5" stroke-linecap="round" stroke-dasharray="46 470"/></g>')

    x = 250
    maxw = W - x - 40
    body += '<g class="k-rise">'
    body += text("@" + login, 15, x, 72, MUTED, "mono", spacing=0.3)
    body += "</g>"
    body += f'<g class="k-rise"{delay(.1)}>' + text(font("bold").fit(name, 52, maxw), 52, x, 128, INK, "bold") + "</g>"
    body += f'<g class="k-rise"{delay(.2)}>' + text(font("medium").fit(bio, 17, maxw), 17, x, 160, MUTED, "medium") + "</g>"
    cx = x
    chips = ""
    for i, label in enumerate(["Software", "Databases", "Systems"]):
        p, w = pill(label, cx, 184, color=ACCENTS[i])
        chips += p
        cx += w + 10
    body += f'<g class="k-rise"{delay(.3)}>{chips}</g>'
    # top-right location + live dot
    body += text(location.upper(), 11, W - 56, 44, DIM, "mono", spacing=1.2, anchor="end")
    body += f'<circle class="k-pulse" cx="{W-40}" cy="40" r="4.5" fill="{RED}"/>'
    return svg(W, h, f"{name} (@{login}) — {bio}", defs, body)


# ── 2. Projects ─────────────────────────────────────────────────────────
def _ago(iso):
    if not iso:
        return ""
    t = dt.datetime.fromisoformat(iso.replace("Z", "+00:00"))
    days = (dt.datetime.now(dt.timezone.utc) - t).days
    if days < 1:
        return "updated today"
    if days < 30:
        return f"updated {days}d ago"
    if days < 365:
        return f"updated {days // 30}mo ago"
    return f"updated {days // 365}y ago"


def projects(repos, total_public):
    cols, gap, pad = 2, 16, 32
    cw = (W - 2 * pad - gap) / cols
    ch = 138
    rows = max(1, math.ceil(len(repos) / cols))
    h = 84 + rows * ch + (rows - 1) * gap + 28
    defs, body = card_frame(W, h)
    body += text("PROJECTS.LIST", 13, pad, 48, RED, "mono", spacing=1.6)
    body += text("~/projects.sh --all", 13, pad + font("mono").width("PROJECTS.LIST", 13, 1.6) + 18, 48, DIM, "mono")
    body += text(f"{total_public} public", 13, W - pad, 48, DIM, "mono", anchor="end")
    body += f'<line x1="{pad}" y1="64" x2="{W-pad}" y2="64" stroke="{LINE}"/>'

    if not repos:
        y = 84
        body += (f'<g class="k-rise"><rect x="{pad}" y="{y}" width="{W-2*pad}" height="{ch}" rx="14" fill="#ffffff" fill-opacity=".02" '
                 f'stroke="{RED}" stroke-opacity=".45" stroke-dasharray="6 6"/>')
        body += text("No public projects yet", 20, pad + 26, y + 58, INK, "bold")
        body += text("New repositories will show up here automatically.", 14, pad + 26, y + 86, MUTED, "medium")
        cur_x = pad + 26 + font("bold").width("No public projects yet", 20) + 8
        body += f'<rect class="k-blink" x="{cur_x:.1f}" y="{y+42}" width="10" height="20" fill="{RED}"/></g>'
        return svg(W, h, "Projects", defs, body)

    for i, r in enumerate(repos):
        col, row = i % cols, i // cols
        x = pad + col * (cw + gap)
        y = 84 + row * (ch + gap)
        acc = ACCENTS[i % len(ACCENTS)]
        g = f'<g class="k-rise"{delay(i * .08)}>'
        g += (f'<rect x="{x:.1f}" y="{y}" width="{cw:.1f}" height="{ch}" rx="14" fill="#ffffff" fill-opacity=".025" '
              f'stroke="#ffffff" stroke-opacity=".08"/>')
        g += f'<rect x="{x+20:.1f}" y="{y+18}" width="22" height="3" rx="1.5" fill="{acc}"/>'
        name = font("bold").fit(r["name"], 18, cw - 40)
        g += text(name, 18, x + 20, y + 48, INK, "bold")
        desc = r.get("description") or "No description yet."
        for j, line in enumerate(font("medium").wrap(desc, 13, cw - 40, 2)):
            g += text(line, 13, x + 20, y + 72 + j * 18, MUTED, "medium")
        fy = y + ch - 20
        fx = x + 20
        lang = r.get("language")
        if lang:
            g += f'<circle cx="{fx+5:.1f}" cy="{fy-4}" r="5" fill="{acc}"/>'
            g += text(lang, 12, fx + 16, fy, MUTED, "mono")
            fx += 16 + font("mono").width(lang, 12) + 18
        g += f'<path d="{star_path(fx+6, fy-4.5, 6.5, 2.8)}" fill="{CORAL}"/>'
        g += text(str(r.get("stars", 0)), 12, fx + 17, fy, MUTED, "mono")
        g += text(_ago(r.get("pushed_at")), 12, x + cw - 20, fy, DIM, "mono", anchor="end")
        g += "</g>"
        body += g
    return svg(W, h, "Projects", defs, body)


# ── 3. Stats ────────────────────────────────────────────────────────────
def stats(stars, contributions, repos, followers):
    h = 236
    defs, body = card_frame(W, h)
    pad, gap = 32, 16
    body += text("Profile Signal", 24, pad, 52, INK, "bold")
    body += text("Live GitHub stats · updated automatically", 13, pad, 76, MUTED, "medium")
    tiles = [("Stars", stars, 50, RED), ("Contributions", contributions, 500, CORAL),
             ("Repositories", repos, 30, ROSE), ("Followers", followers, 50, CRIMSON)]
    tw = (W - 2 * pad - 3 * gap) / 4
    y = 100
    th = 108
    for i, (label, value, target, acc) in enumerate(tiles):
        x = pad + i * (tw + gap)
        g = f'<g class="k-rise"{delay(.1 + i * .08)}>'
        g += (f'<rect x="{x:.1f}" y="{y}" width="{tw:.1f}" height="{th}" rx="14" fill="#ffffff" fill-opacity=".025" '
              f'stroke="#ffffff" stroke-opacity=".08"/>')
        g += text(label, 13, x + 18, y + 30, MUTED, "medium")
        g += text(f"{value:,}", 34, x + 18, y + 72, acc, "bold")
        track = tw - 36
        ratio = max(0.06, min(1.0, math.log1p(value) / math.log1p(target)))
        g += f'<rect x="{x+18:.1f}" y="{y+86}" width="{track:.1f}" height="5" rx="2.5" fill="#ffffff" fill-opacity=".08"/>'
        g += (f'<rect class="k-grow" x="{x+18:.1f}" y="{y+86}" width="{track*ratio:.1f}" height="5" rx="2.5" fill="{acc}"'
              f'{delay(.35 + i * .08)}/>')
        g += "</g>"
        body += g
    return svg(W, h, f"GitHub stats: {stars} stars, {contributions} contributions, {repos} repos, {followers} followers", defs, body)


# ── 4. Contribution heatmap ─────────────────────────────────────────────
def heatmap(weeks, total):
    """weeks: list of weeks, each a list of (date_iso, count) Sunday→Saturday."""
    h = 236
    defs, body = card_frame(W, h)
    pad = 32
    body += text("Contribution Activity", 22, pad, 50, INK, "bold")
    body += text(f"{total:,} contributions in the last year", 13, pad, 74, MUTED, "medium")
    # legend
    lx = W - pad - 5 * 15 - font("mono").width("More", 11) - 6
    body += text("Less", 11, lx - 8, 56, DIM, "mono", anchor="end")
    for i, c in enumerate(HEAT):
        body += f'<rect x="{lx + i*15}" y="46" width="11" height="11" rx="2.5" fill="{c}"/>'
    body += text("More", 11, lx + 5 * 15 + 4, 56, DIM, "mono")

    weeks = weeks[-53:]
    counts = sorted(c for w in weeks for _, c in w if c > 0)

    def level(c):
        if c <= 0 or not counts:
            return 0
        q = [counts[int(len(counts) * p)] for p in (0.25, 0.5, 0.75)]
        return 1 if c <= q[0] else 2 if c <= q[1] else 3 if c <= q[2] else 4

    cell, step = 11, 14.5
    grid_w = len(weeks) * step - (step - cell)
    x0 = (W - grid_w) / 2
    y0 = 118
    month_seen = None
    for wi, week in enumerate(weeks):
        x = x0 + wi * step
        if week:
            m = week[0][0][5:7]
            if m != month_seen and week[0][0][8:10] <= "07":
                label = dt.date(2000, int(m), 1).strftime("%b")
                if wi < len(weeks) - 2:
                    body += text(label, 10, x, y0 - 10, DIM, "mono")
                month_seen = m
        col = f'<g class="k-in"{delay(wi * 0.018)}>'
        for di, (_, c) in enumerate(week):
            lv = level(c)
            col += f'<rect x="{x:.1f}" y="{y0 + di*step:.1f}" width="{cell}" height="{cell}" rx="2.5" fill="{HEAT[lv]}"/>'
        body += col + "</g>"
    return svg(W, h, f"{total} contributions in the last year", defs, body)


# ── 5. Space shooter: a ship flies under the contribution grid and shoots it ──
def shooter(weeks, total, max_targets=90):
    import random
    h = 300
    defs, body = card_frame(W, h)
    pad = 32
    defs += f"""
  <linearGradient id="hull" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="#ffe4e4"/><stop offset="1" stop-color="{RED}"/></linearGradient>
  <linearGradient id="beam" x1="0" y1="1" x2="0" y2="0"><stop offset="0" stop-color="{CORAL}" stop-opacity="0"/><stop offset="1" stop-color="#fff"/></linearGradient>
  <filter id="lg" x="-100%" y="-100%" width="300%" height="300%"><feGaussianBlur stdDeviation="2.2"/></filter>"""
    body += text("SPACE.SHOOTER", 13, pad, 48, RED, "mono", spacing=1.6)
    body += text("~/contributions --destroy", 13, pad + font("mono").width("SPACE.SHOOTER", 13, 1.6) + 18, 48, DIM, "mono")
    body += text(f"{total:,} contributions", 13, W - pad, 48, DIM, "mono", anchor="end")
    body += f'<line x1="{pad}" y1="64" x2="{W-pad}" y2="64" stroke="{LINE}"/>'

    weeks = weeks[-53:]
    cell, step = 11, 14.5
    grid_w = len(weeks) * step - (step - cell)
    x0, y0 = (W - grid_w) / 2, 88
    counts = sorted(c for w in weeks for _, c in w if c > 0)

    def level(c):
        if c <= 0 or not counts:
            return 0
        q = [counts[int(len(counts) * p)] for p in (0.25, 0.5, 0.75)]
        return 1 if c <= q[0] else 2 if c <= q[1] else 3 if c <= q[2] else 4

    cells = []
    for wi, week in enumerate(weeks):
        for di, (_, c) in enumerate(week):
            cells.append((wi, di, level(c)))
    targets = [t for t in cells if t[2] > 0]
    rnd = random.Random(42)
    if len(targets) < 24:  # quiet year: turn some empty cells into dim "asteroids"
        empty = [t for t in cells if t[2] == 0]
        rnd.shuffle(empty)
        targets += [(wi, di, -1) for wi, di, _ in empty[:36 - len(targets)]]
    if len(targets) > max_targets:
        rnd.shuffle(targets)
        targets = targets[:max_targets]
    # visit targets left→right, sweeping rows back and forth, like a real player
    targets.sort(key=lambda t: (t[0] // 4, t[1] if (t[0] // 4) % 2 == 0 else -t[1], t[0]))
    tset = {(wi, di): lv for wi, di, lv in targets}

    ship_y = y0 + 7 * step + 46
    dt, travel, intro = 0.22, 0.28, 0.8
    T = intro + len(targets) * dt + travel + 2.4
    pct = lambda s: f"{100 * s / T:.3f}%"
    css = ""

    # static (never hit) cells
    for wi, di, lv in cells:
        if (wi, di) in tset:
            continue
        body += f'<rect x="{x0 + wi*step:.1f}" y="{y0 + di*step:.1f}" width="{cell}" height="{cell}" rx="2.5" fill="{HEAT[lv]}"/>'

    ship_frames = [f"0% {{ transform: translateX({W/2:.1f}px); }}"]
    for k, (wi, di, lv) in enumerate(targets):
        cx = x0 + wi * step + cell / 2
        cy = y0 + di * step + cell / 2
        fire = intro + k * dt
        hit = fire + travel * (ship_y - cy) / (ship_y - y0)
        color = "#3a2a2d" if lv < 0 else HEAT[lv]
        body += f'<rect x="{cx - cell/2:.1f}" y="{cy - cell/2:.1f}" width="{cell}" height="{cell}" rx="2.5" fill="{HEAT[0]}"/>'
        ship_frames.append(f"{pct(fire)} {{ transform: translateX({cx:.1f}px); }}")
        # target cell: explodes when hit, respawns at the end of the loop
        css += (f"@keyframes c{k} {{ 0%,{pct(hit)} {{ opacity:1; transform:scale(1); }} "
                f"{pct(hit + .12)} {{ opacity:0; transform:scale(1.9); }} 96% {{ opacity:0; transform:scale(.4); }} "
                f"100% {{ opacity:1; transform:scale(1); }} }}\n")
        body += (f'<rect style="animation:c{k} {T:.2f}s linear infinite;transform-box:fill-box;transform-origin:center" '
                 f'x="{cx - cell/2:.1f}" y="{cy - cell/2:.1f}" width="{cell}" height="{cell}" rx="2.5" fill="{color}"/>')
        # laser bolt
        dist = ship_y - 16 - cy
        css += (f"@keyframes b{k} {{ 0%,{pct(fire)} {{ opacity:0; transform:translateY(0); }} "
                f"{pct(fire + .01)} {{ opacity:1; transform:translateY(0); }} "
                f"{pct(hit)} {{ opacity:1; transform:translateY(-{dist:.1f}px); }} "
                f"{pct(hit + .01)},100% {{ opacity:0; transform:translateY(-{dist:.1f}px); }} }}\n")
        body += (f'<rect style="animation:b{k} {T:.2f}s linear infinite;opacity:0" x="{cx-1.2:.1f}" y="{ship_y-26:.1f}" '
                 f'width="2.4" height="12" rx="1.2" fill="url(#beam)"/>')
        # spark burst
        css += (f"@keyframes s{k} {{ 0%,{pct(hit)} {{ opacity:0; transform:scale(.2); }} "
                f"{pct(hit + .02)} {{ opacity:1; transform:scale(1); }} {pct(hit + .3)},100% {{ opacity:0; transform:scale(2.2); }} }}\n")
        body += (f'<circle style="animation:s{k} {T:.2f}s ease-out infinite;opacity:0;transform-box:fill-box;transform-origin:center" '
                 f'cx="{cx:.1f}" cy="{cy:.1f}" r="7" fill="none" stroke="{CORAL}" stroke-width="1.6"/>')
    ship_frames.append(f"{pct(intro + len(targets)*dt + travel + .6)},100% {{ transform: translateX({W/2:.1f}px); }}")
    css += "@keyframes ship { " + " ".join(ship_frames) + " }\n"
    css += f".ship {{ animation: ship {T:.2f}s cubic-bezier(.45,.05,.55,.95) infinite; }}\n"
    css += ".flame { animation: flame .12s steps(2) infinite; transform-box: fill-box; transform-origin: top center; }\n"
    css += "@keyframes flame { 50% { transform: scaleY(.55); } }\n"
    css += "@media (prefers-reduced-motion: reduce) { .ship, .flame, [style*='animation'] { animation: none !important; opacity: 1; } }\n"

    # the ship (drawn around x=0, moved by .ship)
    ship = (
        f'<g class="ship"><g transform="translate(0 {ship_y:.1f})">'
        f'<path class="flame" d="M-4,10 L0,22 L4,10 Z" fill="{CORAL}" filter="url(#lg)"/>'
        f'<path class="flame" d="M-2.5,10 L0,17 L2.5,10 Z" fill="#fff"/>'
        f'<path d="M0,-16 L5,-5 L5,2 L15,9 L15,12 L5,9 L3,12 L-3,12 L-5,9 L-15,12 L-15,9 L-5,2 L-5,-5 Z" fill="url(#hull)"/>'
        f'<path d="M0,-16 L5,-5 L5,2 L15,9 L15,12 L5,9 L3,12 L-3,12 L-5,9 L-15,12 L-15,9 L-5,2 L-5,-5 Z" fill="none" stroke="{BLOOD}" stroke-width=".8"/>'
        f'<ellipse cx="0" cy="-4" rx="2" ry="3.5" fill="#1a0d10"/>'
        f"</g></g>"
    )
    body += ship
    # stars in the background
    stars = "".join(
        f'<circle class="k-pulse" style="animation-delay:{rnd.random()*2.4:.2f}s" cx="{rnd.uniform(pad, W-pad):.1f}" '
        f'cy="{rnd.uniform(y0 + 7*step + 8, h - 14):.1f}" r="{rnd.choice([.6, .8, 1.1])}" fill="#fff" fill-opacity=".5"/>'
        for _ in range(26))
    body = body.replace(ship, stars + ship)
    return svg(W, h, f"Space shooter destroying {total} contributions", defs, body, css)
