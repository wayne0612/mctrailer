"""Normalize McDonald's MCP tool responses into clean, typed structures.

The MCP wraps its JSON inside a markdown-ish text block (content[].text) and
may also expose structuredContent. These helpers pull the embedded JSON out
and shape it for the poster, WITHOUT inventing any field. When data is
missing, callers render a '尚未实时核价 / 实时数据不可用' fallback instead.

Verified shapes (against live mcd-mcp, 2026-10-23):
  query-nearby-stores.data[] -> {storeCode, storeName, address, distance, reservation, beCode}
  query-meals.data.categories[].meals[] -> {code, tags[]}   (NO name/price)
  query-meal-detail.data -> {code, name, image, rounds[].choices[].name}
  calculate-price.data -> {price(fen), originalPrice(fen), discount(fen), productList[]}
"""
from __future__ import annotations

import json
import re
from datetime import datetime

_JSON_RE = re.compile(r'\{"success".*\}', re.DOTALL)


def _extract_json(raw: dict | str | None) -> dict | None:
    if raw is None:
        return None
    if isinstance(raw, str):
        m = _JSON_RE.search(raw)
        return json.loads(m.group(0)) if m else None
    sc = raw.get("structuredContent")
    if isinstance(sc, dict) and "data" in sc:
        return sc
    texts = [c.get("text", "") for c in raw.get("content", []) if c.get("type") == "text"]
    m = _JSON_RE.search("\n".join(texts))
    return json.loads(m.group(0)) if m else None


def _data(raw):
    j = _extract_json(raw)
    return j.get("data") if isinstance(j, dict) else None


def _now() -> str:
    return datetime.now().strftime("%Y-%m-%d %H:%M")


def _yuan(fen):
    try:
        return round(float(fen) / 100, 2)
    except (TypeError, ValueError):
        return None


def normalize_stores(raw) -> list[dict]:
    rows = _data(raw)
    out = []
    for s in (rows if isinstance(rows, list) else []):
        if not isinstance(s, dict):
            continue
        out.append({
            "store_code": s.get("storeCode"),
            "be_code": s.get("beCode"),
            "name": s.get("storeName"),
            "address": s.get("address"),
            "distance": s.get("distance"),
            "reservation": bool(s.get("reservation")),
        })
    return out


def normalize_meals(raw) -> list[dict]:
    """Flatten query-meals categories[].meals[] into a flat code list."""
    d = _data(raw)
    out: list[dict] = []
    if isinstance(d, dict):
        cats = d.get("categories")
        if isinstance(cats, list):
            for cat in cats:
                if not isinstance(cat, dict):
                    continue
                cname = cat.get("name")
                for m in (cat.get("meals") or []):
                    if isinstance(m, dict):
                        out.append({"code": m.get("code"), "category": cname,
                                    "tags": m.get("tags") or []})
    elif isinstance(d, list):
        for m in d:
            if isinstance(m, dict):
                out.append({"code": m.get("code"), "category": None, "tags": m.get("tags") or []})
    return out


def normalize_meal_detail(raw) -> dict:
    d = _data(raw)
    if not isinstance(d, dict):
        return {}
    components = [ch.get("name") for r in (d.get("rounds") or [])
                  for ch in (r.get("choices") or []) if ch.get("name")]
    return {"code": d.get("code"), "name": d.get("name"),
            "image": d.get("image"), "components": components}


def normalize_price(raw) -> dict:
    d = _data(raw)
    if not isinstance(d, dict):
        return {"available": False, "queried_at": _now()}
    j = _extract_json(raw) or {}
    return {
        "available": True,
        "items": [{"code": p.get("productCode"), "name": p.get("productName"),
                   "quantity": p.get("quantity")} for p in (d.get("productList") or [])],
        "total": _yuan(d.get("originalPrice")),
        "discount": _yuan(d.get("discount")),
        "payable": _yuan(d.get("price")),
        "take_ways": [t.get("title") for t in (d.get("takeWayList") or [])],
        "queried_at": j.get("datetime") or _now(),
    }


def normalize_campaign(raw) -> list[dict]:
    rows = _data(raw)
    out = []
    for c in (rows if isinstance(rows, list) else []):
        if isinstance(c, dict):
            out.append({"date": c.get("date") or c.get("activityDate"),
                        "title": c.get("title") or c.get("activityTitle"),
                        "content": c.get("content") or c.get("activityContent"),
                        "image": c.get("image") or c.get("imageUrl")})
    return out
