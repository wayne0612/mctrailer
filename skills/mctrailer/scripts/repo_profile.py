"""Extract a PUBLIC GitHub repo profile and map it to a movie genre.

Deterministic and side-effect free apart from read-only GitHub REST calls.
We only read PUBLIC metadata (description, language, topics, README, recent
commit messages). We never clone, execute, or read private data. If GitHub is
unreachable, callers get a degraded profile so the poster can still render.
"""
from __future__ import annotations

import json
import os
import re
import urllib.error
import urllib.parse
import urllib.request

GENRE_FIX = "fixing_a_bug"        # 悬疑 · Fixing a Bug
GENRE_RELEASE = "release_day"     # 动作 · Release Day
GENRE_REFACTOR = "refactor_marathon"  # 科幻 · Refactor Marathon
GENRE_SIDE = "side_project"       # 公路 · Side Project

# keyword -> genre. Counted over a lowercased text blob.
_KEYWORDS = {
    GENRE_FIX: ["bug", "fix", "patch", "debug", "hotfix", "regression", "crash",
                "panic", "traceback", "issue", "segfault", "leak"],
    GENRE_RELEASE: ["release", "version", "deploy", "launch", "ship", "publish",
                    "changelog", "tag", "v1", "v2", "v3", "stable", "beta"],
    GENRE_REFACTOR: ["refactor", "rewrite", "architecture", "migrate", "optimize",
                     "performance", "overhaul", "cleanup", "monorepo", "typescript migration"],
    GENRE_SIDE: ["experiment", "toy", "playground", "weekend", "side", "personal",
                 "learning", "demo", "template", "awesome", "hello", "starter", "boilerplate"],
}
# tie-break / fallback order
_GENRE_PRIORITY = [GENRE_FIX, GENRE_RELEASE, GENRE_REFACTOR, GENRE_SIDE]

_LANG_ROLE = {
    "typescript": "前端骑士", "javascript": "脚本游侠", "python": "数据法师",
    "rust": "系统工匠", "go": "并发舵手", "c": "底层匠人", "c++": "底层匠人",
    "java": "架构守门人", "kotlin": "安卓信使", "swift": "苹果使者",
    "ruby": "快乐极客", "php": "老站守护", "shell": "自动化杂役",
    "html": "排版学徒", "css": "像素画师", "vue": "渐进派信徒",
}


def parse_repo_url(url: str) -> tuple[str, str]:
    """'https://github.com/owner/repo' -> ('owner', 'repo'). Raises ValueError."""
    m = re.match(r"^https?://github\.com/([^/\s]+)/([^/\s#?]+)", url.strip())
    if not m:
        raise ValueError(f"not a GitHub repo URL: {url!r}")
    return m.group(1), m.group(2).removesuffix(".git")


def classify_genre(text: str, language: str | None = None,
                   topics: list[str] | None = None, commits: list[str] | None = None) -> str:
    """Deterministic genre from a text blob. Pure function (unit-tested)."""
    blob = " ".join(
        [text or "", language or "", " ".join(topics or []), " ".join(commits or [])]
    ).lower()
    blob = re.sub(r"\s+", " ", blob)
    if not blob.strip():
        return GENRE_SIDE
    scores = {g: sum(blob.count(k) for k in kws) for g, kws in _KEYWORDS.items()}
    best = max(scores.values())
    if best <= 0:
        return GENRE_SIDE
    for g in _GENRE_PRIORITY:  # first genre reaching the max score wins
        if scores[g] == best:
            return g
    return GENRE_SIDE


def protagonist_for(language: str | None) -> str:
    return _LANG_ROLE.get((language or "").lower(), "独立开发者")


def _gh_get(path: str, token: str | None = None) -> dict | None:
    url = "https://api.github.com" + path
    req = urllib.request.Request(url)
    req.add_header("Accept", "application/vnd.github+json")
    req.add_header("User-Agent", "mctrailer-skill")
    if token:
        req.add_header("Authorization", "Bearer " + token)
    try:
        with urllib.request.urlopen(req, timeout=20) as resp:
            return json.loads(resp.read().decode("utf-8"))
    except (urllib.error.URLError, urllib.error.HTTPError, json.JSONDecodeError):
        return None


def profile_from_payload(repo: dict, commits: list[str] | None = None) -> dict:
    """Build a normalized profile from a GitHub /repos/{owner}/{repo} payload."""
    name = repo.get("name") or repo.get("full_name") or "unknown"
    desc = repo.get("description") or ""
    lang = repo.get("language")
    topics = repo.get("topics") or []
    stars = int(repo.get("stargazers_count") or 0)
    genre = classify_genre(desc, lang, topics, commits)
    return {
        "full_name": repo.get("full_name") or name,
        "name": name,
        "description": desc,
        "language": lang,
        "topics": topics,
        "stars": stars,
        "commits": commits or [],
        "genre": genre,
        "protagonist": protagonist_for(lang),
        "source": "github-live",
    }


def fetch_repo_profile(url: str, github_token: str | None = None) -> dict:
    """Live path: read public GitHub metadata + a few recent commit messages.

    Unauthenticated GitHub API is limited to 60 req/hour; set env GITHUB_TOKEN
    (a read-only classic token, public_repo scope is enough) to raise it.
    """
    github_token = github_token or os.environ.get("GITHUB_TOKEN")
    owner, repo = parse_repo_url(url)
    data = _gh_get(f"/repos/{owner}/{repo}", github_token)
    if not data:
        raise ConnectionError(f"could not read public metadata for {owner}/{repo}")
    commits: list[str] = []
    cdata = _gh_get(f"/repos/{owner}/{repo}/commits?per_page=5", github_token)
    if isinstance(cdata, list):
        for c in cdata[:5]:
            msg = ((c.get("commit") or {}).get("message") or "").split("\n", 1)[0]
            if msg:
                commits.append(msg)
    prof = profile_from_payload(data, commits)
    prof["url"] = f"https://github.com/{owner}/{repo}"
    return prof


def degraded_profile(url: str) -> dict:
    """Offline fallback profile so the poster still renders (clearly non-live)."""
    try:
        owner, repo = parse_repo_url(url)
    except ValueError:
        owner, repo = "unknown", "unknown"
    name = repo or "unknown"
    return {
        "full_name": f"{owner}/{name}",
        "name": name,
        "description": "",
        "language": None,
        "topics": [],
        "stars": 0,
        "commits": [],
        "genre": GENRE_SIDE,
        "protagonist": "独立开发者",
        "url": url,
        "source": "offline-degraded",
    }
