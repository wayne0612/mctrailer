"""McTrailer vertical slice runner.

public GitHub repo URL -> deterministic movie script -> (optional LIVE
McDonald's MCP menu/price) -> one shareable poster (SVG).

Safety rules enforced here:
  * only PUBLIC GitHub metadata is read (no clone, no execution);
  * MCP calls are best-effort and fully guarded -- any failure degrades to a
    clearly-labelled demo poster instead of faking a price;
  * the token is read from env only and never printed or stored.

Usage:
  python generate.py --repo https://github.com/psf/requests [--city 深圳市 --keyword 南山区] [--demo]
"""
from __future__ import annotations

import argparse
import json
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import repo_profile
import script_engine
import poster as poster_mod
from normalize_mcp import normalize_stores, normalize_meals, normalize_meal_detail, normalize_price
from mcd_client import McdMcpClient, McdMcpError


def _live_supply(client: McdMcpClient, city: str, keyword: str, be_type: int):
    """Best-effort LIVE lookup. Returns (meal_dict, live_flag, queried_at).

    Chain (all verified against live mcd-mcp schemas):
      query-nearby-stores -> storeCode
      query-meals         -> first meal code (categories[].meals[])
      query-meal-detail   -> meal name
      calculate-price     -> payable (fen -> yuan)
    Any step failing degrades gracefully; we never fabricate a name/price.
    """
    stores = normalize_stores(client.call_tool(
        "query-nearby-stores",
        {"beType": be_type, "searchType": 2, "city": city, "keyword": keyword},
    ))
    if not stores:
        return None, False, None
    store = stores[0]
    order_type = 1  # 到店自取 / 得来速
    sc = store.get("store_code")
    meals = normalize_meals(client.call_tool(
        "query-meals", {"storeCode": sc, "orderType": order_type, "beType": be_type}))
    if not meals:
        return None, False, None
    first = meals[0]
    detail = {}
    try:
        detail = normalize_meal_detail(client.call_tool(
            "query-meal-detail",
            {"storeCode": sc, "orderType": order_type, "beType": be_type, "code": first.get("code")}))
    except McdMcpError:
        detail = {}
    price, queried_at = None, None
    try:
        pr = normalize_price(client.call_tool(
            "calculate-price",
            {"storeCode": sc, "orderType": order_type, "beType": be_type,
             "items": [{"productCode": first.get("code"), "quantity": 1}]}))
        price = pr.get("payable")
        queried_at = pr.get("queried_at")
    except McdMcpError:
        price, queried_at = None, None
    meal = {"name": detail.get("name") or "门店人气餐品", "price": price,
            "code": first.get("code"), "store": store.get("name"),
            "components": (detail.get("components") or [])[:3]}
    return meal, True, queried_at


def run(repo_url=None, text=None, scene=None, city=None, keyword="", be_type=1, demo=False) -> dict:
    # 1) build the deterministic script from ONE of three entry points
    if scene:
        script = script_engine.build_script_from_scenario(scene)
        source = "scenario"
    elif text:
        script = script_engine.build_script_from_text(text)
        source = "text"
    else:
        try:
            profile = repo_profile.fetch_repo_profile(repo_url)
        except (ConnectionError, ValueError) as exc:
            print(f"[warn] live GitHub read failed ({exc}); using degraded profile", file=sys.stderr)
            profile = repo_profile.degraded_profile(repo_url)
        script = script_engine.build_script(profile)
        source = profile.get("source")

    # 2) optional LIVE supply
    meal, live, queried_at = None, False, None
    if not demo:
        client = McdMcpClient()
        if not client.has_token():
            print("[info] MCD_MCP_TOKEN not set -> demo poster (no live price)", file=sys.stderr)
        elif not city:
            print("[info] no --city given -> demo poster (nearby lookup needs a city)", file=sys.stderr)
        else:
            try:
                meal, live, queried_at = _live_supply(client, city, keyword, be_type)
            except McdMcpError as exc:
                print(f"[warn] live MCP failed ({exc}); degraded to demo poster", file=sys.stderr)

    # 3) render poster
    svg = poster_mod.render_poster_svg(script, meal=meal, live=live, queried_at=queried_at)
    repo_root = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..", ".."))
    out_dir = os.path.join(repo_root, "media")
    os.makedirs(out_dir, exist_ok=True)
    safe = "".join(c if c.isalnum() else "-" for c in (script.get("repo") or script.get("film_title") or "mctrailer"))[:40]
    out_path = os.path.join(out_dir, f"{safe}-poster.svg")
    with open(out_path, "w", encoding="utf-8") as fh:
        fh.write(svg)

    return {
        "input_kind": "scene" if scene else "text" if text else "repo",
        "profile_source": source,
        "genre": script.get("genre_cn"),
        "film_title": script.get("film_title"),
        "opening_line": script.get("opening_line"),
        "user_quote": script.get("user_quote", ""),
        "protagonist": script.get("protagonist"),
        "meal": meal,
        "live": live,
        "poster": os.path.relpath(out_path),
    }


def main() -> int:
    ap = argparse.ArgumentParser(description="McTrailer: repo URL / one line / scenario -> McDonald's movie poster")
    ap.add_argument("--repo", default=None, help="public GitHub repo URL")
    ap.add_argument("--text", default=None, help="one line about your project/today (no GitHub needed)")
    ap.add_argument("--scene", default=None,
                    choices=["fixing_a_bug", "release_day", "refactor_marathon", "side_project"],
                    help="pick a scenario directly (no GitHub needed)")
    ap.add_argument("--city", default=None, help="city for live nearby-store lookup")
    ap.add_argument("--keyword", default="", help="area keyword for nearby lookup")
    ap.add_argument("--be-type", type=int, default=1, choices=[1, 5], help="1=pickup 5=drive-through")
    ap.add_argument("--demo", action="store_true", help="force demo mode (no MCP call)")
    args = ap.parse_args()
    if not (args.repo or args.text or args.scene):
        ap.error("provide one of --repo / --text / --scene")
    result = run(args.repo, args.text, args.scene, args.city, args.keyword, args.be_type, args.demo)
    print(json.dumps(result, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
