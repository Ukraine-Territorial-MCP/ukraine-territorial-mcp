"""Порівняння українських географічних назв у різних відмінках."""

ADJECTIVE_ENDINGS = (
    "ський", "ського", "ському", "ським",
    "ська", "ської", "ську", "ською",
    "ське", "ського", "ському", "ським",
    "ські", "ських", "ськими",
    "цький", "цького", "цькому", "цьким",
    "цька", "цької", "цьку", "цькою",
    "цьке", "цького", "цькому",
    "цькі", "цьких", "цькими",
)

def normalize_name(name: str) -> str:
    name = name.strip().casefold().replace("’", "'")
    for ending in sorted(ADJECTIVE_ENDINGS, key=len, reverse=True):
        if name.endswith(ending) and len(name) > len(ending) + 2:
            return name[:-len(ending)]
    return name


def names_match(official: str, candidate: str) -> bool:
    official = official.strip().casefold()
    candidate = candidate.strip().casefold()

    if official == candidate:
        return True

    return normalize_name(official) == normalize_name(candidate)


if __name__ == "__main__":
    tests = [
        ("Іванівська", "Іванівської"),
        ("Чернігівський", "Чернігівського"),
        ("Чернігівська", "Чернігівської"),
        ("Київська", "Київської"),
        ("Полтавська", "Полтавської"),
        ("Іванівська", "Київської"),
    ]

    for official, candidate in tests:
        print(
            f"{official} / {candidate}:",
            names_match(official, candidate)
        )
