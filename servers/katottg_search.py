from servers.territory_types import get_territory_type
import json
from pathlib import Path

PATH = Path(__file__).resolve().parents[1] / "data/official/ukraine-katottg.json"

with PATH.open(encoding="utf-8") as f:
    RECORDS = json.load(f)["records"]

BY_CODE = {r["code"]: r for r in RECORDS}

SOURCE_METADATA = {
    "registry": "КАТОТТГ",
    "edition_date": json.loads(
        PATH.read_text(encoding="utf-8")
    )["edition_date"],
}


FIELDS = [
    "region_code",
    "district_code",
    "community_code",
    "settlement_code",
    "additional_code",
]


def find_by_code(code: str) -> dict | None:
    return BY_CODE.get(code.strip().upper())



def search_by_name(query: str, limit: int = 20) -> list[dict]:
    """Пошук за українською назвою, транслітерацією та типом громади."""
    from servers.uk_translit import transliterate

    query = query.strip().casefold()
    if not query:
        return []

    limit = max(1, min(limit, 100))

    normalized = query.replace("-", " ")
    for suffix in (
        "територіальна громада",
        "сільська громада",
        "селищна громада",
        "міська громада",
        "об'єднана територіальна громада",
        "отг",
        "громада",
        "rural community",
        "urban community",
        "territorial community",
        "community",
        "hromada",
    ):
        normalized = normalized.replace(suffix, " ")

    normalized = " ".join(normalized.split())
    if not normalized:
        return []

    matches = []

    for record in RECORDS:
        name_uk = record["name"].casefold()
        name_en = transliterate(record["name"])

        if normalized == name_uk or normalized == name_en:
            score = 0
        elif normalized in name_uk or normalized in name_en:
            score = 1
        else:
            continue

        if any(word in query for word in ("громада", "отг", "community", "hromada")):
            if record["category"] != "H":
                continue

        matches.append((score, record))

    matches.sort(key=lambda item: (item[0], item[1]["name"], item[1]["code"]))
    return [record for _, record in matches[:limit]]


def get_children(code: str) -> list[dict]:
    parent = find_by_code(code)
    if not parent:
        return []

    result = []

    for record in RECORDS:
        if record["code"] == code:
            continue

        chain = list(dict.fromkeys(
            record[field]
            for field in FIELDS
            if record.get(field)
        ))

        if code in chain:
            position = chain.index(code)
            if position == len(chain) - 2:
                result.append(record)

    return result


def search_by_location(
    query: str,
    region: str = "",
    district: str = "",
    limit: int = 20,
) -> list[dict]:
    """Пошук за назвою з фільтрами області та району."""
    from servers.uk_translit import transliterate

    def matches_name(record: dict, value: str) -> bool:
        if not value.strip():
            return True

        value = value.strip().casefold()
        name = record["name"].casefold()
        latin = transliterate(record["name"])

        return value in name or value in latin

    results = search_by_name(query, 100)

    if region:
        results = [
            r for r in results
            if r.get("region_code")
            and (parent := BY_CODE.get(r["region_code"]))
            and matches_name(parent, region)
        ]

    if district:
        results = [
            r for r in results
            if r.get("district_code")
            and (parent := BY_CODE.get(r["district_code"]))
            and matches_name(parent, district)
        ]

    return results[:max(1, min(limit, 100))]


def find_community_settlements(
    query: str,
    region: str = "",
    district: str = "",
) -> dict:
    """Знайти громаду та її населені пункти за назвою."""
    communities = [
        r for r in search_by_location(
            query,
            region=region,
            district=district,
            limit=100,
        )
        if r["category"] == "H"
    ]

    if not communities:
        return {
            "status": "not_found",
            "message": "Громаду не знайдено",
        }

    if len(communities) > 1:
        return {
            "status": "ambiguous",
            "message": "Знайдено кілька громад. Уточніть область або район.",
            "communities": communities,
        }

    community = communities[0]
    settlements = get_children(community["code"])

    return {
        "status": "ok",
        "community": community,
        "settlement_count": len(settlements),
        "settlements": settlements,
    }


def search_detailed(
    query: str,
    region_code: str = "",
    district_code: str = "",
    community_code: str = "",
    offset: int = 0,
    limit: int = 20,
) -> dict:
    """Пошук територій з адміністративними назвами та фільтрами."""
    from servers.uk_translit import transliterate

    from territorial_knowledge import get_hierarchy

    query = query.strip().casefold()
    region_code = region_code.strip().upper()
    district_code = district_code.strip().upper()
    community_code = community_code.strip().upper()

    offset = max(0, int(offset))
    limit = max(1, min(int(limit), 100))

    if not query:
        return {"total": 0, "offset": offset, "limit": limit, "results": []}

    normalized = query.replace("-", " ")

    for suffix in (
        "територіальна громада",
        "сільська громада",
        "селищна громада",
        "міська громада",
        "об'єднана територіальна громада",
        "отг",
        "громада",
        "rural community",
        "urban community",
        "territorial community",
        "community",
        "hromada",
    ):
        normalized = normalized.replace(suffix, " ")

    normalized = " ".join(normalized.split())

    category_names = {
        "O": "Область або Автономна Республіка Крим",
        "P": "Район",
        "H": "Об'єднана територіальна громада",
        "C": "Село",
        "X": "Селище",
        "M": "Місто",
        "B": "Район у місті",
        "K": "Місто зі спеціальним статусом",
    }

    matches = []

    for record in RECORDS:
        if region_code and record.get("region_code") != region_code:
            continue
        if district_code and record.get("district_code") != district_code:
            continue
        if community_code and record.get("community_code") != community_code:
            continue

        name_uk = record["name"].casefold()
        name_en = transliterate(record["name"])

        if normalized == name_uk or normalized == name_en:
            score = 0
        elif normalized in name_uk or normalized in name_en:
            score = 1
        else:
            continue

        if any(word in query for word in ("громада", "отг", "community", "hromada")):
            if record["category"] != "H":
                continue

        matches.append((score, record))

    matches.sort(key=lambda x: (x[0], x[1]["name"], x[1]["code"]))

    total = len(matches)
    page = matches[offset:offset + limit]
    results = []

    for _, record in page:
        hierarchy = get_hierarchy(record["code"])

        def parent_name(category):
            return next(
                (x["name"] for x in hierarchy if x["category"] == category),
                None
            )

        region = parent_name("O")
        district = parent_name("P")
        community = parent_name("H")

        parts = [record["name"]]

        for name in (community, district, region):
            if name and name != record["name"]:
                parts.append(name)

        results.append({
            **record,
            **get_territory_type(record),
            "category_name": category_names.get(record["category"]),
            "region_name": region,
            "district_name": district,
            "community_name": community,
            "display_name": ", ".join(parts),
            "source": SOURCE_METADATA.copy(),
        })

    return {
        "total": total,
        "offset": offset,
        "limit": limit,
        "results": results,
    }
