"""Generate dark/light terminal-style SVGs for a GitHub profile README.

Usage: python3 gen_terminal.py <out_dir>
Static SVG + CSS keyframes only (no JS, no external fonts) so it renders inside GitHub's <img>.
"""
import sys
from pathlib import Path
from xml.sax.saxutils import escape

FONT = "ui-monospace, SFMono-Regular, Menlo, Consolas, 'Liberation Mono', monospace"
FS, LH, CW = 14, 20, 8.43          # font size, line height, approx char width
W, PAD, TOP = 900, 22, 34          # svg width, inner padding, title bar height

THEMES = {
    "dark":  dict(win="#0d1117", border="#30363d", bar="#161b22", title="#8b949e", text="#c9d1d9",
                  dim="#8b949e", prompt="#3fb950", path="#58a6ff", key="#d2a8ff", art="#58a6ff", cursor="#c9d1d9"),
    "light": dict(win="#ffffff", border="#d0d7de", bar="#f6f8fa", title="#57606a", text="#1f2328",
                  dim="#57606a", prompt="#1a7f37", path="#0969da", key="#8250df", art="#0969da", cursor="#1f2328"),
}
PALETTE = ["#f85149", "#d29922", "#3fb950", "#58a6ff", "#bc8cff", "#39c5cf", "#8b949e", "#e6edf3"]

ART = [
    r"                ##         .",
    r"          ## ## ##        ==",
    r"       ## ## ## ## ##    ===",
    r'   /"""""""""""""""""\___/ ===',
    r"  {                       /  ===-",
    r"   \______ O           __/",
    r"     \    \         __/",
    r"      \____\_______/",
]
INFO = [
    ("Name",    "Jason"),
    ("Role",    "Backend Developer"),
    ("OS",      "macOS · OrbStack"),
    ("Langs",   "Java · Python · TypeScript · Shell"),
    ("Backend", "Spring Boot · Kafka · Elasticsearch · ClickHouse"),
    ("DevOps",  "Docker · Compose · GitHub Actions · GHCR"),
    ("Infra",   "Valkey · RabbitMQ · PostgreSQL"),
    ("Observe", "Prometheus · Loki · Tempo · Grafana"),
    ("Network", "sing-box · Cloudflare WARP · gost"),
]
WHOAMI = "jason — backend developer, docker & self-hosting"


def build(t):
    els, css = [], []
    y = TOP + PAD + FS  # first baseline
    tick = [0.4]  # running clock (s)

    def show(at):
        return f"opacity:0;animation:show .01s linear {at:.2f}s forwards"

    def prompt_line(cmd, y):
        at = tick[0]
        p = (f'<text x="{PAD}" y="{y}" style="{show(at)}">'
             f'<tspan fill="{t["prompt"]}">zricky@github</tspan><tspan fill="{t["dim"]}">:</tspan>'
             f'<tspan fill="{t["path"]}">~</tspan><tspan fill="{t["dim"]}">$ </tspan></text>')
        x = PAD + CW * len("zricky@github:~$ ")
        dur = 0.08 * len(cmd)
        c = (f'<text x="{x:.1f}" y="{y}" fill="{t["text"]}" '
             f'style="clip-path:inset(0 100% 0 0);animation:type {dur:.2f}s steps({len(cmd)}) {at + 0.35:.2f}s forwards">'
             f'{escape(cmd)}</text>')
        els.extend([p, c])
        tick[0] = at + 0.35 + dur + 0.25

    # $ whoami
    prompt_line("whoami", y); y += LH
    els.append(f'<text x="{PAD}" y="{y}" fill="{t["text"]}" style="{show(tick[0])}">{escape(WHOAMI)}</text>')
    tick[0] += 0.5; y += LH * 2

    # $ neofetch
    prompt_line("neofetch", y); y += LH
    start = tick[0]
    art_x, info_x = PAD + 8, PAD + CW * 40
    for i, line in enumerate(ART):
        els.append(f'<text x="{art_x}" y="{y + (i + 1) * LH}" fill="{t["art"]}" xml:space="preserve" '
                   f'style="{show(start + i * 0.06)}">{escape(line)}</text>')
    head = "zricky@github"
    els.append(f'<text x="{info_x:.1f}" y="{y}" style="{show(start)}"><tspan fill="{t["prompt"]}" font-weight="bold">'
               f'{head}</tspan></text>')
    els.append(f'<text x="{info_x:.1f}" y="{y + LH}" fill="{t["dim"]}" style="{show(start)}">{"─" * len(head)}</text>')
    for i, (k, v) in enumerate(INFO):
        yy = y + (i + 2) * LH
        els.append(f'<text x="{info_x:.1f}" y="{yy}" xml:space="preserve" style="{show(start + 0.1 + i * 0.07)}">'
                   f'<tspan fill="{t["key"]}" font-weight="bold">{k:<9}</tspan><tspan fill="{t["text"]}">{escape(v)}</tspan></text>')
    pal_y = y + (len(INFO) + 2) * LH - FS + 6
    pal_at = start + 0.1 + len(INFO) * 0.07
    for i, c in enumerate(PALETTE):
        els.append(f'<rect x="{info_x + i * 26:.1f}" y="{pal_y}" width="24" height="12" rx="2" fill="{c}" style="{show(pal_at)}"/>')
    block = max(len(ART), len(INFO) + 3)
    tick[0] = pal_at + 0.5
    y += LH * (block + 1)

    # final prompt + blinking cursor
    at = tick[0]
    els.append(f'<text x="{PAD}" y="{y}" style="{show(at)}"><tspan fill="{t["prompt"]}">zricky@github</tspan>'
               f'<tspan fill="{t["dim"]}">:</tspan><tspan fill="{t["path"]}">~</tspan><tspan fill="{t["dim"]}">$ </tspan></text>')
    cx = PAD + CW * len("zricky@github:~$ ")
    els.append(f'<rect x="{cx:.1f}" y="{y - FS + 2}" width="{CW:.1f}" height="{FS + 2}" fill="{t["cursor"]}" '
               f'style="opacity:0;animation:show .01s linear {at:.2f}s forwards, blink 1s steps(1) {at + 0.5:.2f}s infinite"/>')

    H = y + PAD
    css = (
        "@keyframes show{to{opacity:1}}"
        "@keyframes type{to{clip-path:inset(0 0 0 0)}}"
        "@keyframes blink{50%{opacity:0}}"
        "@media (prefers-reduced-motion:reduce){*{animation:none!important;opacity:1!important;clip-path:none!important}}"
    )
    chrome = (
        f'<rect x=".5" y=".5" width="{W - 1}" height="{H - 1}" rx="10" fill="{t["win"]}" stroke="{t["border"]}"/>'
        f'<path d="M.5 10.5a10 10 0 0 1 10-10h{W - 21}a10 10 0 0 1 10 10v{TOP - 10}h-{W - 1}z" fill="{t["bar"]}"/>'
        f'<line x1=".5" y1="{TOP + .5}" x2="{W - .5}" y2="{TOP + .5}" stroke="{t["border"]}"/>'
        f'<circle cx="20" cy="17" r="6" fill="#ff5f57"/><circle cx="40" cy="17" r="6" fill="#febc2e"/>'
        f'<circle cx="60" cy="17" r="6" fill="#28c840"/>'
        f'<text x="{W / 2}" y="22" text-anchor="middle" fill="{t["title"]}" font-size="12">zricky@github: ~</text>'
    )
    return (f'<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" viewBox="0 0 {W} {H}" '
            f'font-family="{FONT}" font-size="{FS}" role="img" aria-label="zricky@github: whoami → {escape(WHOAMI)}">'
            f'<style>{css}</style>{chrome}{"".join(els)}</svg>\n')


if __name__ == "__main__":
    out = Path(sys.argv[1]); (out / "assets").mkdir(parents=True, exist_ok=True)
    for name, theme in THEMES.items():
        (out / "assets" / f"terminal-{name}.svg").write_text(build(theme), encoding="utf-8")
    print("written:", *sorted(p.name for p in (out / "assets").glob("*.svg")))
