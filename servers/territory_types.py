"""Класифікація територій України на основі КАТОТТГ."""

SPECIAL_CODES = {
    "UA01000000000013043": (
        "autonomous_republic",
        "Автономна республіка",
    ),
    "UA80000000000093317": (
        "special_status_city",
        "Місто зі спеціальним статусом",
    ),
    "UA85000000000065278": (
        "special_status_city",
        "Місто зі спеціальним статусом",
    ),
}

CATEGORY_TYPES = {
    "O": ("oblast", "Область"),
    "P": ("district", "Район"),
    "H": ("community", "Територіальна громада"),
    "M": ("city", "Місто"),
    "X": ("settlement", "Селище"),
    "C": ("village", "Село"),
    "B": ("city_district", "Район у місті"),
}


def get_territory_type(record: dict) -> dict:
    code = record["code"]
    category = record["category"]

    if code in SPECIAL_CODES:
        type_code, type_name = SPECIAL_CODES[code]
    else:
        type_code, type_name = CATEGORY_TYPES[category]

    return {
        "territory_type": type_code,
        "territory_type_name": type_name,
    }
