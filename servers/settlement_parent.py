"""Визначення адміністративної належності населеного пункту."""

from servers.katottg_search import RECORDS, BY_CODE
from servers.uk_translit import transliterate


def find_settlement_parent(
    name: str,
    region: str = "",
    district: str = "",
) -> dict:
    """Пошук населених пунктів та їхніх адміністративних батьків."""

    query = name.strip().casefold()
    region_query = region.strip().casefold()
    district_query = district.strip().casefold()

    if not query:
        return {
            "status": "not_found",
            "matches": [],
            "count": 0,
        }

    def name_matches(record, value):
        if not value:
            return True
        if not record:
            return False

        return (
            record["name"].casefold() == value
            or transliterate(record["name"]).casefold() == value
        )

    matches = []

    for settlement in RECORDS:
        if settlement["category"] not in ("M", "X", "C"):
            continue

        if not name_matches(settlement, query):
            continue

        community = BY_CODE.get(settlement.get("community_code"))
        district_record = BY_CODE.get(settlement.get("district_code"))
        region_record = BY_CODE.get(settlement.get("region_code"))

        if region_query and not name_matches(region_record, region_query):
            continue

        if district_query and not name_matches(district_record, district_query):
            continue

        matches.append({
            "settlement": settlement,
            "community": community,
            "district": district_record,
            "region": region_record,
        })

    return {
        "status": (
            "not_found" if not matches
            else "ok" if len(matches) == 1
            else "ambiguous"
        ),
        "count": len(matches),
        "matches": matches,
    }
