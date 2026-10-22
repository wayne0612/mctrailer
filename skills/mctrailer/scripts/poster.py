"""Render a shareable cinema poster as SVG (stdlib only, no image deps).

The SVG is self-contained and converts to PNG in the browser (see web/). If a
real McDonald's MCP meal/price is supplied it is shown as the hero '补给';
otherwise the poster is clearly labelled 演示样例 (demo) — we never fake a price.
"""
from __future__ import annotations

import html
from datetime import datetime

W, H = 720, 1080

_PALETTES = {
    "noir":  {"bg1": "#14141a", "bg2": "#05050a", "accent": "#e5c07b", "chip": "#2a2a33"},
    "action": {"bg1": "#1e0f0d", "bg2": "#0a0403", "accent": "#ff5f45", "chip": "#331a15"},
    "scifi":  {"bg1": "#07202e", "bg2": "#02080f", "accent": "#4fd1ff", "chip": "#0f3040"},
    "road":   {"bg1": "#1e1608", "bg2": "#0a0703", "accent": "#ffb347", "chip": "#33260f"},
}


def _esc(s: str) -> str:
    return html.escape(str(s), quote=True)


def _wrap(text: str, per_line: int) -> list[str]:
    text = str(text)
    return [text[i:i + per_line] for i in range(0, len(text), per_line)] or [""]


def _now() -> str:
    return datetime.now().strftime("%Y-%m-%d %H:%M")


def render_poster_svg(script: dict, meal: dict | None = None,
                      live: bool = False, queried_at: str | None = None) -> str:
    p = _PALETTES.get(script.get("palette", "road"), _PALETTES["road"])
    stats = script.get("stat_block") or {}
    title = script.get("film_title", "《未命名》")
    line = script.get("opening_line", "")
    protagonist = script.get("protagonist", "独立开发者")
    prop = script.get("prop_line", "")
    genre_cn = script.get("genre_cn", "")
    repo_url = script.get("repo_url", "")
    badge_text = "实时 MCP · 官方菜单" if live else "演示样例 · 非实时核价"
    badge_fill = "#1f7a4d" if live else "#4a4a52"
    ts = queried_at or _now()

    parts: list[str] = []
    parts.append(f'<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" '
                 f'viewBox="0 0 {W} {H}" font-family="PingFang SC, Microsoft YaHei, sans-serif">')
    # background
    parts.append(f'<defs><linearGradient id="bg" x1="0" y1="0" x2="0" y2="1">'
                 f'<stop offset="0" stop-color="{p["bg1"]}"/><stop offset="1" stop-color="{p["bg2"]}"/>'
                 f'</linearGradient></defs>')
    parts.append(f'<rect width="{W}" height="{H}" fill="url(#bg)"/>')
    # accent frame + top bar
    parts.append(f'<rect x="28" y="28" width="{W-56}" height="{H-56}" fill="none" '
                 f'stroke="{p["accent"]}" stroke-opacity="0.35" stroke-width="2" rx="10"/>')
    parts.append(f'<rect x="28" y="28" width="{W-56}" height="8" fill="{p["accent"]}" rx="4"/>')

    # genre badge (top-left) + live/demo badge (top-right)
    parts.append(f'<rect x="56" y="66" width="240" height="40" rx="20" fill="{p["chip"]}"/>')
    parts.append(f'<text x="76" y="92" font-size="22" fill="{p["accent"]}">{_esc(genre_cn)}</text>')
    parts.append(f'<rect x="{W-56-150}" y="66" width="150" height="40" rx="20" fill="{badge_fill}"/>')
    parts.append(f'<text x="{W-56-150+18}" y="92" font-size="18" fill="#ffffff">{_esc(badge_text)}</text>')

    # brand
    parts.append(f'<text x="56" y="150" font-size="20" fill="{p["accent"]}" letter-spacing="4">McTrailer · 麦门导演局</text>')

    # film title (wrapped, large)
    y = 250
    parts.append(f'<text x="56" y="{y}" font-size="52" font-weight="700" fill="#ffffff">{_esc(_wrap(title, 9)[0])}</text>')
    for extra in _wrap(title, 9)[1:]:
        y += 62
        parts.append(f'<text x="56" y="{y}" font-size="52" font-weight="700" fill="#ffffff">{_esc(extra)}</text>')

    # opening line
    y += 66
    for seg in _wrap(line, 16):
        parts.append(f'<text x="56" y="{y}" font-size="26" fill="{p["accent"]}" font-style="italic">{_esc(seg)}</text>')
        y += 36

    # user's own words (text mode) as a personal quote
    user_quote = script.get("user_quote", "")
    if user_quote:
        y += 6
        for seg in _wrap("— " + user_quote + " —", 20):
            parts.append(f'<text x="56" y="{y}" font-size="18" fill="#8a8a9a" font-style="italic">{_esc(seg)}</text>')
            y += 26

    # protagonist chip + prop line
    y += 26
    parts.append(f'<rect x="56" y="{y-30}" width="300" height="44" rx="22" fill="{p["chip"]}" '
                 f'stroke="{p["accent"]}" stroke-opacity="0.4"/>')
    parts.append(f'<text x="76" y="{y}" font-size="22" fill="#ffffff">主角：{_esc(protagonist)}</text>')
    y += 58
    for seg in _wrap(prop, 18):
        parts.append(f'<text x="56" y="{y}" font-size="20" fill="#c9c9d2">{_esc(seg)}</text>')
        y += 30

    # stat block (only shown when real repo data exists)
    y += 20
    if stats:
        stars_phrase = stats.get("stars_phrase", "0 stars")
        lang = stats.get("language", "未知语言")
        parts.append(f'<text x="56" y="{y}" font-size="20" fill="#9a9aa6">'
                     f'主语言 {_esc(lang)} · {_esc(stars_phrase)}</text>')
    else:
        parts.append(f'<text x="56" y="{y}" font-size="18" fill="#6f6f80">— 麦门导演局 · 今日放映 —</text>')

    # meal / supply card
    card_y = H - 300
    parts.append(f'<rect x="48" y="{card_y}" width="{W-96}" height="200" rx="16" '
                 f'fill="#000000" fill-opacity="0.35" stroke="{p["accent"]}" stroke-opacity="0.5"/>')
    parts.append(f'<text x="76" y="{card_y+44}" font-size="22" fill="{p["accent"]}">今日补给 · 麦门套餐</text>')
    if meal and meal.get("name"):
        name = meal.get("name")
        price = meal.get("price")
        price_txt = f"¥{price}" if price not in (None, "") else "价格以门店实时为准"
        parts.append(f'<text x="76" y="{card_y+96}" font-size="34" font-weight="700" fill="#ffffff">{_esc(name)}</text>')
        parts.append(f'<text x="76" y="{card_y+140}" font-size="26" fill="{p["accent"]}">{_esc(price_txt)}</text>')
        src = "来源：麦当劳 MCP 实时" if live else "来源：演示样例数据"
    else:
        parts.append(f'<text x="76" y="{card_y+96}" font-size="28" fill="#d8d8e0">补给餐品生成中…</text>')
        parts.append(f'<text x="76" y="{card_y+140}" font-size="22" fill="#9a9aa6">尚未实时核价 · 配置 MCP Token 后显示真实菜单与价格</text>')
        src = "来源：麦当劳 MCP（未连接）"
    parts.append(f'<text x="76" y="{card_y+180}" font-size="16" fill="#8a8a96">{_esc(src)} · 查询时间 {_esc(ts)}</text>')

    # footer
    parts.append(f'<text x="56" y="{H-52}" font-size="16" fill="#7a7a86">{_esc(repo_url[:70])}</text>')
    parts.append(f'<text x="{W-56}" y="{H-52}" font-size="16" fill="#7a7a86" text-anchor="end">github.com/M-China/mcd-mcp-server</text>')

    parts.append("</svg>")
    return "\n".join(parts)


if __name__ == "__main__":
    demo_script = {
        "film_title": "《demo：部署前 15 分钟》", "opening_line": "“倒计时开始。”",
        "protagonist": "数据法师", "prop_line": "上线前的最后冲刺。", "palette": "action",
        "genre_cn": "动作 · Release Day", "stat_block": {"language": "Python", "stars_phrase": "1.2k stars"},
        "repo_url": "https://github.com/acme/demo", "source": "demo",
    }
    print(render_poster_svg(demo_script, meal=None, live=False)[:200])
