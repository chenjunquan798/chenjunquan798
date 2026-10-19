"""Generate the self-hosted GitHub stats card (light + dark).

Data source: GitHub REST API. No third-party services, so the card renders
even when badge/CDN providers are unreachable.

Run:  GH_TOKEN=... python scripts/gen_stats.py
"""

import json
import os
import sys
import urllib.error
import urllib.request
from pathlib import Path
from xml.sax.saxutils import escape

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "assets"
LOGIN = "chenjunquan798"
API = "https://api.github.com"

THEMES = {
    "light": dict(
        text="#0b1220", muted="#57606a", a1="#0969da", a2="#8250df",
        track="#e7ebf0", border="#d0d7de", bg="none",
    ),
    "dark": dict(
        text="#e6edf3", muted="#8b949e", a1="#58a6ff", a2="#bc8cff",
        track="#21262d", border="#30363d", bg="none",
    ),
}


def api(path: str):
    req = urllib.request.Request(API + path)
    token = os.environ.get("GH_TOKEN")
    if token:
        req.add_header("Authorization", "Bearer " + token)
    req.add_header("Accept", "application/vnd.github+json")
    req.add_header("User-Agent", "profile-stats")
    try:
        with urllib.request.urlopen(req, timeout=45) as r:
            return json.loads(r.read().decode())
    except urllib.error.HTTPError as e:
        body = e.read().decode()[:200]
        print(f"warn: {path} -> {e.code} {body}", file=sys.stderr)
        return None


def collect():
    user = api(f"/users/{LOGIN}") or {}
    repos, page = [], 1
    while page <= 3:
        batch = api(f"/users/{LOGIN}/repos?per_page=100&page={page}&type=owner") or []
        repos.extend(batch)
        if len(batch) < 100:
            break
        page += 1

    # The profile repository itself is not a project — keep it out of the numbers.
    repos = [r for r in repos if r.get("name", "").lower() != LOGIN.lower()]

    stars = sum(r.get("stargazers_count", 0) for r in repos)
    langs: dict[str, int] = {}
    for r in repos:
        lang = r.get("language")
        if lang:
            langs[lang] = langs.get(lang, 0) + 1

    commits = 0
    search = api(f"/search/commits?q=author:{LOGIN}&per_page=1")
    if search:
        commits = search.get("total_count", 0)

    return {
        "repos": len(repos),
        "stars": stars,
        "followers": user.get("followers", 0),
        "commits": commits,
        "langs": sorted(langs.items(), key=lambda kv: (-kv[1], kv[0]))[:3],
        "lang_total": sum(langs.values()),
    }


def card(data: dict, theme: str) -> str:
    t = THEMES[theme]
    p = []
    add = p.append
    font = "Inter, 'Segoe UI', 'Helvetica Neue', Arial, sans-serif"

    add(
        '<svg xmlns="http://www.w3.org/2000/svg" width="1000" height="232" '
        'viewBox="0 0 1000 232" role="img" aria-labelledby="st">'
    )
    add(f'<title id="st">{escape(LOGIN)} — public activity</title>')
    add("<defs>")
    add(
        f'<linearGradient id="bar" x1="0" y1="0" x2="1" y2="0">'
        f'<stop offset="0" stop-color="{t["a1"]}"/>'
        f'<stop offset="1" stop-color="{t["a2"]}"/></linearGradient>'
    )
    add("</defs>")
    add(
        f'<rect x="0.5" y="0.5" width="999" height="231" rx="14" fill="{t["bg"]}" '
        f'stroke="{t["border"]}"/>'
    )

    add(
        f'<text x="36" y="52" fill="{t["muted"]}" font-family="{font}" font-size="11" '
        'letter-spacing="2.4" font-weight="600">PUBLIC ACTIVITY</text>'
    )

    metrics = [
        ("Projects", data["repos"]),
        ("Stars earned", data["stars"]),
        ("Commits", data["commits"]),
        ("Followers", data["followers"]),
    ]
    for i, (label, value) in enumerate(metrics):
        col, row = i % 2, i // 2
        x = 36 + col * 210
        y = 104 + row * 76
        add(
            f'<text x="{x}" y="{y}" fill="{t["text"]}" font-family="{font}" '
            f'font-size="32" font-weight="700">{value:,}</text>'
        )
        add(
            f'<text x="{x}" y="{y + 22}" fill="{t["muted"]}" font-family="{font}" '
            f'font-size="12">{escape(label)}</text>'
        )

    add(
        f'<line x1="470" y1="40" x2="470" y2="192" stroke="{t["border"]}" '
        'stroke-width="1"/>'
    )

    add(
        f'<text x="512" y="52" fill="{t["muted"]}" font-family="{font}" font-size="11" '
        'letter-spacing="2.4" font-weight="600">LANGUAGES \u00b7 BY REPOSITORY</text>'
    )

    if data["langs"]:
        total = max(data["lang_total"], 1)
        for i, (name, count) in enumerate(data["langs"]):
            y = 96 + i * 44
            pct = count / total
            add(
                f'<text x="512" y="{y}" fill="{t["text"]}" font-family="{font}" '
                f'font-size="13" font-weight="600">{escape(name)}</text>'
            )
            add(
                f'<text x="962" y="{y}" fill="{t["muted"]}" font-family="{font}" '
                f'font-size="12" text-anchor="end">{pct * 100:.0f}%</text>'
            )
            add(
                f'<rect x="512" y="{y + 8}" width="450" height="4" rx="2" '
                f'fill="{t["track"]}"/>'
            )
            add(
                f'<rect x="512" y="{y + 8}" width="{max(450 * pct, 3):.0f}" height="4" '
                f'rx="2" fill="url(#bar)"/>'
            )
    else:
        add(
            f'<text x="512" y="100" fill="{t["muted"]}" font-family="{font}" '
            f'font-size="13">No public projects yet.</text>'
        )
        add(
            f'<text x="512" y="124" fill="{t["muted"]}" font-family="{font}" '
            f'font-size="12">This card fills in as projects land.</text>'
        )

    add("</svg>")
    return "\n".join(p) + "\n"


def main() -> None:
    data = collect()
    print(
        f"repos={data['repos']} stars={data['stars']} "
        f"commits={data['commits']} followers={data['followers']} "
        f"langs={data['langs']}"
    )
    for theme in ("light", "dark"):
        path = OUT / f"stats-{theme}.svg"
        path.write_text(card(data, theme), encoding="utf-8")
        print("wrote", path.relative_to(ROOT))


if __name__ == "__main__":
    main()
