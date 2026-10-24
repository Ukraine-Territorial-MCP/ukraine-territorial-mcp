"""Підрахунок міст, селищ і сіл за адміністративною територією."""

from collections import Counter
from servers.katottg_search import RECORDS, BY_CODE
from servers.uk_translit import transliterate

LEVELS = {
    "region": ("O", "region_code"),
    "district": ("P", "district_code"),
    "community": ("H", "community_code"),
}

def count_settlements(
    level: str = "ukraine",
    name: str = "",
    code: str = "",
    region: str = "",
    district: str = "",
) -> dict:
    """Підрахунок населених пунктів України за категоріями КАТОТТГ."""

    level = level.strip().casefold()
    name = name.strip().casefold()
    code = code.strip().upper()
    region = region.strip().casefold()
    district = district.strip().casefold()

    if level not in ("ukraine", *LEVELS):
        return {"status": "invalid_level", "allowed_levels": ["ukraine", *LEVELS]}

    def matches(record, query):
        if not query:
            return True
        if not record:
            return False
        return (
            record["name"].casefold() == query
            or transliterate(record["name"]).casefold() == query
        )

    def totals(items):
        counts = Counter(r["category"] for r in items)
        return {
            "cities": counts["M"],
            "settlements": counts["X"],
            "villages": counts["C"],
            "total": len(items),
        }

    settlements = [
        r for r in RECORDS
        if r["category"] in ("M", "X", "C")
    ]

    if level == "ukraine":
        return {
            "status": "ok",
            "level": "ukraine",
            "counts": totals(settlements),
        }

    category, field = LEVELS[level]

    if not name and not code:
        return {
            "status": "missing_identifier",
            "message": "Укажіть назву або код КАТОТТГ території.",
        }

    candidates = []

    for record in RECORDS:
        if record["category"] != category:
            continue
        if code and record["code"] != code:
            continue
        if name and not matches(record, name):
            continue
        if region and not matches(BY_CODE.get(record.get("region_code")), region):
            continue
        if district and not matches(BY_CODE.get(record.get("district_code")), district):
            continue
        candidates.append(record)

    if not candidates:
        return {"status": "not_found", "matches": [], "count": 0}

    results = []

    for record in candidates:
        items = [r for r in settlements if r.get(field) == record["code"]]
        results.append({
            "territory": record,
            "counts": totals(items),
        })

    return {
        "status": "ok" if len(results) == 1 else "ambiguous",
        "level": level,
        "count": len(results),
        "matches": results,
    }
