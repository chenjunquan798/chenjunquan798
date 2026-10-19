"""Generate the profile hero assets (light + dark).

Geometry is shared between both themes; only the palette changes, so the two
renderings stay pixel-identical in layout when GitHub switches colour schemes.

Run:  python scripts/gen_assets.py
"""

from pathlib import Path
from xml.sax.saxutils import escape

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "assets"
OUT.mkdir(parents=True, exist_ok=True)

NAME = "chenjunquan798"
ROLE = "Applied AI \u00b7 retrieval, agents, evaluation"
EYEBROW = "AI / LLM ENGINEERING"
URL_TEXT = "github.com/chenjunquan798"

THEMES = {
    "light": {
        "bg1": "#ffffff",
        "bg2": "#eef2f7",
        "grid": "#d0d7de",
        "grid_op": "0.55",
        "text": "#0b1220",
        "muted": "#57606a",
        "a1": "#0969da",
        "a2": "#8250df",
        "edge": "#8c959f",
        "edge_op": "0.38",
        "halo_op": "0.10",
        "border": "#d0d7de",
    },
    "dark": {
        "bg1": "#0b0f14",
        "bg2": "#141b24",
        "grid": "#30363d",
        "grid_op": "0.45",
        "text": "#e6edf3",
        "muted": "#8b949e",
        "a1": "#58a6ff",
        "a2": "#bc8cff",
        "edge": "#6e7681",
        "edge_op": "0.45",
        "halo_op": "0.12",
        "border": "#21262d",
    },
}

# A small deterministic graph — reads as a knowledge graph, not decoration.
POINTS = [
    (792, 150), (852, 96), (866, 214), (930, 140), (944, 268), (1008, 88),
    (1020, 196), (1086, 142), (1100, 250), (1162, 96), (1172, 190), (1218, 282),
]
EDGES = [
    (0, 1), (0, 2), (1, 3), (2, 3), (2, 4), (3, 5), (3, 6), (4, 6), (5, 7),
    (6, 7), (6, 8), (7, 9), (7, 10), (8, 10), (9, 10), (10, 11),
]
HUBS = {3, 7, 10}  # nodes that get a halo + accent fill


def hero(theme_name: str) -> str:
    t = THEMES[theme_name]
    p: list[str] = []
    add = p.append

    add(
        '<svg xmlns="http://www.w3.org/2000/svg" width="1280" height="340" '
        'viewBox="0 0 1280 340" role="img" aria-labelledby="t d">'
    )
    add(f"<title id=\"t\">{escape(NAME)} \u2014 {escape(ROLE)}</title>")
    add(
        '<desc id="d">Profile banner: name, role, and a connected-node motif '
        "representing retrieval and agent graphs.</desc>"
    )

    # ---- defs -----------------------------------------------------------
    add("<defs>")
    add(
        f'<linearGradient id="bg" x1="0" y1="0" x2="1" y2="1">'
        f'<stop offset="0" stop-color="{t["bg1"]}"/>'
        f'<stop offset="1" stop-color="{t["bg2"]}"/></linearGradient>'
    )
    add(
        f'<linearGradient id="accent" x1="0" y1="0" x2="1" y2="0">'
        f'<stop offset="0" stop-color="{t["a1"]}"/>'
        f'<stop offset="1" stop-color="{t["a2"]}"/></linearGradient>'
    )
    add(
        f'<radialGradient id="glow" cx="0.5" cy="0.5" r="0.5">'
        f'<stop offset="0" stop-color="{t["a1"]}" stop-opacity="0.30"/>'
        f'<stop offset="1" stop-color="{t["a1"]}" stop-opacity="0"/>'
        "</radialGradient>"
    )
    add(
        '<pattern id="grid" width="40" height="40" patternUnits="userSpaceOnUse">'
        f'<path d="M40 0H0V40" fill="none" stroke="{t["grid"]}" '
        f'stroke-width="1" stroke-opacity="{t["grid_op"]}"/></pattern>'
    )
    add(
        '<linearGradient id="gridFade" x1="0" y1="0" x2="1" y2="0">'
        '<stop offset="0" stop-color="#ffffff" stop-opacity="0.9"/>'
        '<stop offset="0.55" stop-color="#ffffff" stop-opacity="0.55"/>'
        '<stop offset="1" stop-color="#ffffff" stop-opacity="0.12"/>'
        "</linearGradient>"
    )
    add(
        '<mask id="gridMask">'
        '<rect width="1280" height="340" fill="url(#gridFade)"/>'
        "</mask>"
    )
    add(
        '<linearGradient id="rail" x1="0" y1="0" x2="0" y2="1">'
        f'<stop offset="0" stop-color="{t["a1"]}"/>'
        f'<stop offset="1" stop-color="{t["a2"]}"/>'
        "</linearGradient>"
    )
    add("</defs>")

    # ---- background -----------------------------------------------------
    add('<rect width="1280" height="340" fill="url(#bg)"/>')
    add('<g mask="url(#gridMask)"><rect width="1280" height="340" fill="url(#grid)"/></g>')
    add('<circle cx="980" cy="70" r="380" fill="url(#glow)"/>')
    add('<rect x="0" y="0" width="3" height="340" fill="url(#rail)"/>')

    # ---- node motif -----------------------------------------------------
    add(f'<g stroke="{t["edge"]}" stroke-opacity="{t["edge_op"]}" stroke-width="1.2">')
    for a, b in EDGES:
        x1, y1 = POINTS[a]
        x2, y2 = POINTS[b]
        add(f'<line x1="{x1}" y1="{y1}" x2="{x2}" y2="{y2}"/>')
    add("</g>")

    for i in HUBS:
        x, y = POINTS[i]
        add(
            f'<circle cx="{x}" cy="{y}" r="26" fill="{t["a1"]}" '
            f'opacity="{t["halo_op"]}"/>'
        )

    for i, (x, y) in enumerate(POINTS):
        if i in HUBS:
            add(f'<circle cx="{x}" cy="{y}" r="5.5" fill="{t["a2"]}"/>')
            add(
                f'<circle cx="{x}" cy="{y}" r="5.5" fill="none" '
                f'stroke="{t["a1"]}" stroke-opacity="0.55"/>'
            )
        else:
            add(
                f'<circle cx="{x}" cy="{y}" r="3.6" fill="{t["bg1"]}" '
                f'stroke="{t["a1"]}" stroke-opacity="0.85" stroke-width="1.4"/>'
            )

    # ---- copy -----------------------------------------------------------
    font = "Inter, 'Segoe UI', 'Helvetica Neue', Arial, sans-serif"
    mono = "'JetBrains Mono', 'Cascadia Code', Consolas, monospace"

    add(
        f'<text x="72" y="96" fill="{t["a1"]}" font-family="{font}" font-size="13" '
        'font-weight="600" letter-spacing="3.4">'
        f"{escape(EYEBROW)}</text>"
    )
    add(
        f'<text x="70" y="176" fill="{t["text"]}" font-family="{font}" '
        'font-size="60" font-weight="700" letter-spacing="-1.6">'
        f"{escape(NAME)}</text>"
    )
    add(
        '<rect x="72" y="196" width="64" height="3" rx="1.5" fill="url(#accent)"/>'
    )
    add(
        f'<text x="72" y="230" fill="{t["muted"]}" font-family="{font}" '
        f'font-size="19">{escape(ROLE)}</text>'
    )
    add(
        f'<text x="72" y="272" fill="{t["muted"]}" font-family="{mono}" '
        'font-size="13" letter-spacing="0.4">'
        f"{escape(URL_TEXT)}</text>"
    )

    # hairline frame
    add(
        f'<rect x="0.5" y="0.5" width="1279" height="339" fill="none" '
        f'stroke="{t["border"]}" stroke-opacity="0.9"/>'
    )
    add("</svg>")
    return "\n".join(p) + "\n"


def main() -> None:
    for name in ("light", "dark"):
        path = OUT / f"hero-{name}.svg"
        path.write_text(hero(name), encoding="utf-8")
        print(f"wrote {path.relative_to(ROOT)} ({path.stat().st_size} bytes)")


if __name__ == "__main__":
    main()
