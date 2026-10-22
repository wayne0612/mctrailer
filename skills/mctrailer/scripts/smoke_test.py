"""McTrailer smoke test — offline, deterministic, no token required.

Verifies the whole vertical slice using canned (demo) inputs:
  GitHub payload -> profile -> genre -> script -> poster(SVG).
Plus deterministic genre-mapping checks. Exit code 0 = PASS.
"""
from __future__ import annotations

import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import repo_profile
import script_engine
import poster as poster_mod

_PASS = 0
_FAIL = 0


def check(name: str, cond: bool, detail: str = "") -> None:
    global _PASS, _FAIL
    if cond:
        _PASS += 1
        print(f"  PASS  {name}")
    else:
        _FAIL += 1
        print(f"  FAIL  {name}  {detail}")


def main() -> int:
    print("[smoke] genre mapping (deterministic)")
    check("bug keywords -> fixing_a_bug",
          repo_profile.classify_genre("fix a nasty bug in parser", "Python", ["hotfix"]) == repo_profile.GENRE_FIX)
    check("release keywords -> release_day",
          repo_profile.classify_genre("v2 release deploy", "Go", ["changelog"]) == repo_profile.GENRE_RELEASE)
    check("refactor keywords -> refactor_marathon",
          repo_profile.classify_genre("big refactor of the architecture", "TypeScript", ["migrate"]) == repo_profile.GENRE_REFACTOR)
    check("empty text -> side_project",
          repo_profile.classify_genre("") == repo_profile.GENRE_SIDE)
    check("toy keywords -> side_project",
          repo_profile.classify_genre("my weekend side project playground", "JS") == repo_profile.GENRE_SIDE)

    print("[smoke] determinism (same input -> same output)")
    p1 = repo_profile.profile_from_payload(
        {"name": "demo", "description": "fix bug", "language": "Python", "stargazers_count": 12, "topics": ["hotfix"]},
        ["fix: crash on startup"])
    p2 = repo_profile.profile_from_payload(
        {"name": "demo", "description": "fix bug", "language": "Python", "stargazers_count": 12, "topics": ["hotfix"]},
        ["fix: crash on startup"])
    s1 = script_engine.build_script(p1)
    s2 = script_engine.build_script(p2)
    check("build_script deterministic", s1 == s2, f"{s1} != {s2}")
    check("protagonist from language", p1["protagonist"] == "数据法师", p1["protagonist"])

    print("[smoke] poster render")
    svg = poster_mod.render_poster_svg(s1, meal=None, live=False)
    check("svg is well-formed envelope",
          svg.startswith("<svg") and svg.rstrip().endswith("</svg>"))
    check("demo poster labelled", "演示样例" in svg)
    check("no price fabricated in demo", "¥" not in svg)

    svg_live = poster_mod.render_poster_svg(s1, meal={"name": "巨无霸", "price": 23.5}, live=True)
    check("live poster shows price", "¥23.5" in svg_live and "实时 MCP" in svg_live)

    # write a sample poster for media/
    repo_root = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..", ".."))
    out_dir = os.path.join(repo_root, "media")
    os.makedirs(out_dir, exist_ok=True)
    with open(os.path.join(out_dir, "smoke-sample.svg"), "w", encoding="utf-8") as fh:
        fh.write(svg)
    print(f"[smoke] sample poster -> {os.path.relpath(os.path.join(out_dir, 'smoke-sample.svg'))}")

    print(f"\n[smoke] RESULT: {_PASS} passed, {_FAIL} failed")
    return 1 if _FAIL else 0


if __name__ == "__main__":
    raise SystemExit(main())
