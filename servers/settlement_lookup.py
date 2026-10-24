"""Пошук громади через назву населеного пункту."""

from servers.katottg_search import RECORDS, BY_CODE, get_children
from servers.uk_translit import transliterate


def find_communities_by_settlement(
    name: str,
    region_code: str = "",
    district_code: str = "",
) -> dict:
    """Знайти громади за точною назвою населеного пункту."""

    query = name.strip().casefold()

    if not query:
        return {"status": "not_found", "communities": []}

    settlements = [
        r for r in RECORDS
        if r["category"] in ("M", "X", "C")
        and (
            r["name"].casefold() == query
            or transliterate(r["name"]).casefold() == query
        )
        and (not region_code or r["region_code"] == region_code)
        and (not district_code or r["district_code"] == district_code)
    ]

    communities = {}

    for settlement in settlements:
        community = BY_CODE.get(settlement["community_code"])

        if community and community["category"] == "H":
            communities[community["code"]] = community

    results = list(communities.values())

    if not results:
        return {"status": "not_found", "communities": []}

    if len(results) > 1:
        return {
            "status": "ambiguous",
            "communities": results,
        }

    community = results[0]
    children = get_children(community["code"])

    return {
        "status": "ok",
        "community": community,
        "settlement_count": len(children),
        "settlements": children,
    }


if __name__ == "__main__":
    for name in ("Bakhchysarai", "Lviv", "Odesa", "Chernihiv", "Ivanivka"):
        result = find_communities_by_settlement(name)
        print(
            name,
            "→",
            result["status"],
            "|",
            result.get("community", {}).get("name", ""),
            "| варіантів:",
            len(result.get("communities", [])),
        )
