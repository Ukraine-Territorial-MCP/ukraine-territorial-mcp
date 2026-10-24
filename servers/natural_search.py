"""Пошук громад та їхніх населених пунктів за текстовим запитом."""

import re

from servers.katottg_search import (
    RECORDS,
    get_children,
)
from servers.name_matching import names_match
from servers.settlement_lookup import find_communities_by_settlement
from servers.uk_translit import transliterate


def matches(official: str, candidate: str) -> bool:
    if names_match(official, candidate):
        return True
    return transliterate(official).casefold() == candidate.casefold()



def extract_region_codes(query: str):
    """Визначити область за українською або англійською назвою."""
    patterns = [
        r"([\wʼ’'-]+)\s+област(?:ь|і|ю|ей|ями|ях)\b",
        r"([\w'-]+)\s+(?:oblast|region)\b",
    ]

    for pattern in patterns:
        match = re.search(pattern, query, re.IGNORECASE)
        if not match:
            continue

        name = match.group(1)
        codes = set()

        for record in RECORDS:
            if record["category"] != "O":
                continue

            if matches(record["name"], name):
                codes.add(record["code"])
                continue

            latin = transliterate(record["name"]).casefold()
            candidate = name.casefold()

            # Англійські географічні назви без прикметникового закінчення.
            if re.search(r"\b(?:oblast|region)\b", query, re.IGNORECASE):
                variants = {latin}
                if latin == "odeska":
                    variants.add("odesa")
                for suffix in ("tska", "ska", "zka"):
                    if latin.endswith(suffix):
                        variants.add(latin[:-len(suffix)])

                if candidate in variants:
                    codes.add(record["code"])

        return codes

    return None




def matches_district(official: str, candidate: str) -> bool:
    """Порівняти офіційну назву району з англійським варіантом."""
    if matches(official, candidate):
        return True

    latin = transliterate(official).casefold()
    candidate = candidate.casefold()
    variants = {latin}

    for suffix in ("skyi", "zkyi", "tskyi"):
        if latin.endswith(suffix):
            stem = latin[:-len(suffix)]
            variants.add(stem)
            variants.add(stem + "a")

    if latin == "odeskyi":
        variants.add("odesa")

    return candidate in variants


def search_community_in_text(query: str) -> dict:
    """Визначити громаду з тексту, враховуючи район."""
    patterns = [
        (
            r"([\wʼ’'-]+)\s+громад[аиіуою]\b",
            r"([\wʼ’'-]+)\s+район[ауіом]*\b",
        ),
        (
            r"([\w'-]+)\s+(?:rural\s+|territorial\s+)?community\b",
            r"([\w'-]+)\s+district\b",
        ),
    ]

    community_name = None
    district_name = None

    for community_pattern, district_pattern in patterns:
        community_match = re.search(
            community_pattern, query, re.IGNORECASE
        )
        district_match = re.search(
            district_pattern, query, re.IGNORECASE
        )

        if community_match:
            community_name = community_match.group(1)
            if district_match:
                district_name = district_match.group(1)
            break

    if not community_name:
        return {
            "status": "not_recognized",
            "message": "Не вдалося розпізнати назву громади.",
        }

    communities = [
        r for r in RECORDS
        if r["category"] == "H"
        and matches(r["name"], community_name)
    ]

    if district_name:
        districts = [
            r for r in RECORDS
            if r["category"] == "P"
            and matches_district(r["name"], district_name)
        ]
        district_codes = {r["code"] for r in districts}
        communities = [
            r for r in communities
            if r["district_code"] in district_codes
        ]

    region_codes = extract_region_codes(query)

    if region_codes is not None:
        communities = [
            r for r in communities
            if r["region_code"] in region_codes
        ]

    if not communities:
        district_codes = None

        if district_name:
            district_codes = {
                r["code"] for r in RECORDS
                if r["category"] == "P"
                and matches_district(r["name"], district_name)
            }

        if (region_codes is None or region_codes) and (
            district_codes is None or district_codes
        ):
            fallback = find_communities_by_settlement(community_name)

            candidates = (
                [fallback["community"]]
                if fallback["status"] == "ok"
                else fallback.get("communities", [])
            )

            communities = [
                r for r in candidates
                if (region_codes is None or r["region_code"] in region_codes)
                and (
                    district_codes is None
                    or r["district_code"] in district_codes
                )
            ]

    if not communities:
        return {
            "status": "not_found",
            "message": "Громаду за цим запитом не знайдено.",
        }

    if len(communities) > 1:
        options = []

        for community in communities:
            settlements = get_children(community["code"])
            options.append({
                **community,
                "settlement_count": len(settlements),
                "settlement_examples": [
                    {
                        "name": settlement["name"],
                        "code": settlement["code"],
                        "category": settlement["category"],
                    }
                    for settlement in settlements[:5]
                ],
            })

        return {
            "status": "ambiguous",
            "message": (
                "Знайдено кілька громад із такою назвою. "
                "Оберіть потрібну за кодом КАТОТТГ "
                "або населеними пунктами."
            ),
            "communities": options,
        }

    community = communities[0]
    settlements = get_children(community["code"])

    return {
        "status": "ok",
        "community": community,
        "settlement_count": len(settlements),
        "settlements": settlements,
    }


if __name__ == "__main__":
    queries = [
        "Покажи всі села Іванівської громади Чернігівського району",
        "Іванівська громада Чернігівський район",
        "Ivanivska Community Chernihivskyi District",
    ]

    for query in queries:
        result = search_community_in_text(query)
        print("\nЗапит:", query)
        print("Статус:", result["status"])
        if result["status"] == "ok":
            print("Громада:", result["community"]["name"])
            print("КАТОТТГ:", result["community"]["code"])
            print("Населених пунктів:", result["settlement_count"])
        else:
            print(result.get("message"))
