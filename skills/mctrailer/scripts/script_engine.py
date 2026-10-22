"""Deterministic 'movie script' generator for McTrailer.

Given a repo profile, produce a cinema-poster script: film title, opening
line, protagonist, prop line and a stat block. Fully deterministic — the same
profile always yields the same script (unit-tested over fixed samples).
Entertainment classification only: never a judgement of a programmer's skill.
"""
from __future__ import annotations

from repo_profile import (
    GENRE_FIX,
    GENRE_RELEASE,
    GENRE_REFACTOR,
    GENRE_SIDE,
)

# Each template: (中文片名模板, 电影台词, 视觉色调key, 道具行)
_TEMPLATES = {
    GENRE_FIX: {
        "film": "《{name}：第 37 次修复》",
        "line": "“第 37 次修复，终于通过。”",
        "palette": "noir",
        "prop": "深夜的屏幕微光，是悬疑片最好的打光。",
        "genre_cn": "悬疑 · Fixing a Bug",
    },
    GENRE_RELEASE: {
        "film": "《{name}：部署前 15 分钟》",
        "line": "“倒计时开始，谁也别拦我上线。”",
        "palette": "action",
        "prop": "发布会前的最后 15 分钟，比动作片更刺激。",
        "genre_cn": "动作 · Release Day",
    },
    GENRE_REFACTOR: {
        "film": "《{name}：重构纪元》",
        "line": "“重构不是毁灭，而是新生。”",
        "palette": "scifi",
        "prop": "当旧架构化作星尘，新世界从 commit 里升起。",
        "genre_cn": "科幻 · Refactor Marathon",
    },
    GENRE_SIDE: {
        "film": "《{name}：一个人的公路》",
        "line": "“踩下油门，去向只有代码知道。”",
        "palette": "road",
        "prop": "没有 KPI 的周末，一个 side project 就是整条公路。",
        "genre_cn": "公路 · Side Project",
    },
}


def _stars_phrase(stars: int) -> str:
    if stars >= 1000:
        return f"{stars / 1000:.1f}k stars"
    return f"{stars} stars"


def build_script(profile: dict) -> dict:
    """Turn a repo profile into a deterministic poster script."""
    genre = profile.get("genre") or GENRE_SIDE
    tpl = _TEMPLATES.get(genre, _TEMPLATES[GENRE_SIDE])
    name = profile.get("name") or "unknown"
    lang = profile.get("language") or "未知语言"
    stars = int(profile.get("stars") or 0)
    commits = profile.get("commits") or []
    protagonist = profile.get("protagonist") or "独立开发者"

    return {
        "genre": genre,
        "genre_cn": tpl["genre_cn"],
        "film_title": tpl["film"].format(name=name),
        "opening_line": tpl["line"],
        "protagonist": protagonist,
        "prop_line": tpl["prop"],
        "palette": tpl["palette"],
        "stat_block": {
            "language": lang,
            "stars": stars,
            "stars_phrase": _stars_phrase(stars),
            "recent_commits": commits[:3],
        },
        "source": profile.get("source", "unknown"),
        "repo": profile.get("full_name") or name,
        "repo_url": profile.get("url", ""),
    }


if __name__ == "__main__":  # tiny manual demo
    import json
    demo = {"name": "demo-repo", "genre": GENRE_FIX, "language": "Python",
            "stars": 42, "commits": ["fix: flaky test"], "protagonist": "数据法师",
            "full_name": "acme/demo-repo", "source": "demo"}
    print(json.dumps(build_script(demo), ensure_ascii=False, indent=2))
