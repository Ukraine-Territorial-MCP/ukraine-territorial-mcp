"""Спрощена українська транслітерація для пошуку КАТОТТГ."""

MAP = {
    "а": "a", "б": "b", "в": "v", "г": "h", "ґ": "g",
    "д": "d", "е": "e", "є": "ie", "ж": "zh", "з": "z",
    "и": "y", "і": "i", "ї": "i", "й": "i", "к": "k",
    "л": "l", "м": "m", "н": "n", "о": "o", "п": "p",
    "р": "r", "с": "s", "т": "t", "у": "u", "ф": "f",
    "х": "kh", "ц": "ts", "ч": "ch", "ш": "sh",
    "щ": "shch", "ь": "", "ю": "iu", "я": "ia",
    "'": "", "’": "", "ʼ": "",
}

INITIAL = {
    "є": "ye",
    "ї": "yi",
    "й": "y",
    "ю": "yu",
    "я": "ya",
}

def transliterate(text: str) -> str:
    result = []
    at_word_start = True

    for char in text.lower():
        if char.isalpha():
            if at_word_start and char in INITIAL:
                result.append(INITIAL[char])
            else:
                result.append(MAP.get(char, char))
            at_word_start = False
        else:
            result.append(MAP.get(char, char))
            if char not in ("'", "’", "ʼ"):
                at_word_start = True

    return "".join(result)


if __name__ == "__main__":
    for name in ["Количівка", "Іванівська", "Чернігівська", "Ягідне"]:
        print(name, "→", transliterate(name))
