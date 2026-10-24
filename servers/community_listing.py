"""Перелік територіальних громад за областю або районом."""

from servers.katottg_search import RECORDS, BY_CODE
from servers.uk_translit import transliterate


def list_communities(
    region: str = "",
    district: str = "",
    region_code: str = "",
    district_code: str = "",
) -> dict:
    """Знайти громади за адміністративною належністю."""

    region = region.strip().casefold()
    district = district.strip().casefold()
    region_code = region_code.strip().upper()
    district_code = district_code.strip().upper()

    if not any((region, district, region_code, district_code)):
        return {
            "status": "missing_filter",
            "message": "Укажіть область або район (назву чи код КАТОТТГ).",
        }

    def name_matches(record, query):
        if not query or not record:
            return not query
        value = record["name"].casefold()
        return (
            value == query
            or transliterate(record["name"]).casefold() == query
        )

    matched = []

    for record in RECORDS:
        if record["category"] != "H":
            continue

        region_record = BY_CODE.get(record["region_code"])
        district_record = BY_CODE.get(record["district_code"])

        if region_code and record["region_code"] != region_code:
            continue
        if district_code and record["district_code"] != district_code:
            continue
        if not name_matches(region_record, region):
            continue
        if not name_matches(district_record, district):
            continue

        matched.append({
            "name": record["name"],
            "code": record["code"],
            "district": district_record["name"] if district_record else None,
            "district_code": record["district_code"],
            "region": region_record["name"] if region_record else None,
            "region_code": record["region_code"],
        })

    matched.sort(key=lambda item: (
        item["region"] or "",
        item["district"] or "",
        item["name"],
        item["code"],
    ))

    return {
        "status": "ok" if matched else "not_found",
        "count": len(matched),
        "communities": matched,
    }
