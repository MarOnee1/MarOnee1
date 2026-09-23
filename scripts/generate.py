"""Fetch public GitHub data and redraw the live profile cards.

Run by .github/workflows/snake.yml. Usage:
    python scripts/generate.py --out dist            # real data (needs GITHUB_TOKEN)
    python scripts/generate.py --out dist --mock     # sample data for previews
"""
import argparse
import base64
import datetime as dt
import json
import os
import random
import sys
import urllib.request

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import live_cards  # noqa: E402

API = "https://api.github.com"
QUERY = """
query($login: String!) {
  user(login: $login) {
    login name bio location avatarUrl(size: 264)
    followers { totalCount }
    pinnedItems(first: 4, types: REPOSITORY) {
      nodes { ... on Repository { name description stargazerCount pushedAt isFork primaryLanguage { name } } }
    }
    repositories(first: 100, ownerAffiliations: OWNER, privacy: PUBLIC,
                 orderBy: {field: PUSHED_AT, direction: DESC}) {
      totalCount
      nodes { name description stargazerCount pushedAt isFork primaryLanguage { name } }
    }
    contributionsCollection {
      contributionCalendar {
        totalContributions
        weeks { contributionDays { date contributionCount } }
      }
    }
  }
}"""


def _request(url, token, data=None):
    headers = {"User-Agent": "maronee1-profile-cards", "Accept": "application/vnd.github+json"}
    if token:
        headers["Authorization"] = f"Bearer {token}"
    body = json.dumps(data).encode() if data is not None else None
    req = urllib.request.Request(url, data=body, headers=headers)
    with urllib.request.urlopen(req, timeout=30) as r:
        return r.read(), r.headers.get("Content-Type", "")


def _repo(n):
    return {"name": n["name"], "description": n.get("description"),
            "stars": n.get("stargazerCount", n.get("stargazers_count", 0)),
            "pushed_at": n.get("pushedAt", n.get("pushed_at")),
            "language": (n.get("primaryLanguage") or {}).get("name") if "primaryLanguage" in n else n.get("language"),
            "fork": n.get("isFork", n.get("fork", False))}


def fetch(login, token):
    data = {"user": {"login": login}, "repos": [], "public": 0, "stars": 0,
            "followers": 0, "weeks": [], "total": 0, "avatar": None}
    try:
        raw, _ = _request(f"{API}/graphql", token, {"query": QUERY, "variables": {"login": login}})
        u = json.loads(raw)["data"]["user"]
        data["user"] = {k: u.get(k) for k in ("login", "name", "bio", "location")}
        data["avatar_url"] = u.get("avatarUrl")
        data["followers"] = u["followers"]["totalCount"]
        all_repos = [_repo(n) for n in u["repositories"]["nodes"]]
        pinned = [_repo(n) for n in u["pinnedItems"]["nodes"] if n]
        data["public"] = u["repositories"]["totalCount"]
        data["stars"] = sum(r["stars"] for r in all_repos)
        data["repos"] = pinned or all_repos
        cal = u["contributionsCollection"]["contributionCalendar"]
        data["total"] = cal["totalContributions"]
        data["weeks"] = [[(d["date"], d["contributionCount"]) for d in w["contributionDays"]] for w in cal["weeks"]]
    except Exception as e:  # fall back to the REST API (no contribution calendar there)
        print(f"GraphQL failed ({e}); falling back to REST", file=sys.stderr)
        try:
            u = json.loads(_request(f"{API}/users/{login}", token)[0])
            data["user"] = {k: u.get(k) for k in ("login", "name", "bio", "location")}
            data["avatar_url"] = u.get("avatar_url")
            data["followers"] = u.get("followers", 0)
            data["public"] = u.get("public_repos", 0)
            repos = json.loads(_request(f"{API}/users/{login}/repos?per_page=100&sort=pushed", token)[0])
            data["repos"] = [_repo(r) for r in repos]
            data["stars"] = sum(r["stars"] for r in data["repos"])
        except Exception as e2:
            print(f"REST failed too ({e2}); drawing empty cards", file=sys.stderr)

    # never show the profile repo itself or forks
    data["repos"] = [r for r in data["repos"] if r["name"].lower() != login.lower() and not r["fork"]][:4]
    if data.get("avatar_url"):
        try:
            url = data["avatar_url"] + ("&" if "?" in data["avatar_url"] else "?") + "s=264"
            raw, ctype = _request(url, None)
            mime = ctype.split(";")[0] or "image/png"
            data["avatar"] = f"data:{mime};base64,{base64.b64encode(raw).decode()}"
        except Exception as e:
            print(f"Avatar download failed ({e})", file=sys.stderr)
    if not data["weeks"]:
        data["weeks"] = empty_year()
    return data


def empty_year():
    today = dt.date.today()
    start = today - dt.timedelta(days=364 + (today.weekday() + 1) % 7)
    weeks, day = [], start
    while day <= today:
        week = []
        for _ in range(7):
            if day <= today:
                week.append((day.isoformat(), 0))
            day += dt.timedelta(days=1)
        weeks.append(week)
    return weeks


def mock(login):
    random.seed(7)
    weeks = [[(d, (random.random() < 0.35) * random.randint(1, 9)) for d, _ in w] for w in empty_year()]
    return {"user": {"login": login, "name": None, "bio": None, "location": None}, "avatar": None,
            "followers": 3, "public": 4, "stars": 7,
            "repos": [
                {"name": "tienda-online", "description": "Prototype online store with events, built for the Soluciones Informáticas course.", "stars": 3, "pushed_at": "2026-09-20T10:00:00Z", "language": "JavaScript", "fork": False},
                {"name": "mips-playground", "description": "Small MIPS assembly exercises: loops, arrays and syscalls.", "stars": 2, "pushed_at": "2026-06-02T10:00:00Z", "language": "Assembly", "fork": False},
                {"name": "oracle-sql-labs", "description": "Database design and queries for the Base de Datos course project.", "stars": 1, "pushed_at": "2026-05-11T10:00:00Z", "language": "PLSQL", "fork": False},
                {"name": "estadistica-r", "description": None, "stars": 1, "pushed_at": "2026-09-17T10:00:00Z", "language": "R", "fork": False},
            ],
            "weeks": weeks, "total": sum(c for w in weeks for _, c in w)}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", default="dist")
    ap.add_argument("--mock", action="store_true")
    ap.add_argument("--empty", action="store_true", help="preview a brand-new account")
    args = ap.parse_args()
    login = os.environ.get("USERNAME_OVERRIDE") or os.environ.get("GITHUB_REPOSITORY_OWNER") or "maronee1"
    token = os.environ.get("GITHUB_TOKEN")
    d = mock(login) if args.mock else fetch(login, token)
    if args.empty:
        d.update(repos=[], public=0, stars=0, followers=0, total=0, weeks=empty_year())
    os.makedirs(args.out, exist_ok=True)
    files = {
        "hero.svg": live_cards.hero(d["user"], d["avatar"]),
        "projects.svg": live_cards.projects(d["repos"], d["public"]),
        "stats.svg": live_cards.stats(d["stars"], d["total"], d["public"], d["followers"]),
        "heatmap.svg": live_cards.heatmap(d["weeks"], d["total"]),
        "shooter.svg": live_cards.shooter(d["weeks"], d["total"]),
    }
    for name, content in files.items():
        with open(os.path.join(args.out, name), "w", encoding="utf-8") as f:
            f.write(content)
        print(f"wrote {name} ({len(content)//1024} KB)")


if __name__ == "__main__":
    main()
