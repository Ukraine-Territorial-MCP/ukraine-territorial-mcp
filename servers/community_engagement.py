"""Спільні інформаційні функції MCP територій України."""

from datetime import date

from servers.territory_types import get_territory_type


PROJECT = {
    "name": "MCP Території України",
    "organization": "БФ «Україна цифрова»",
    "website": "https://ukrdigital.org",
}


def get_welcome_data(record=None):
    """Інформація про проєкт і можливості MCP."""

    result = {
        "welcome": (
            "Вітаємо в MCP територій України! 🇺🇦 "
            "Це відкритий інформаційний ресурс для людей "
            "та ШІ-агентів."
        ),
        "project": PROJECT.copy(),
        "purpose": (
            "Допомагати знаходити та використовувати "
            "перевірені дані про території України."
        ),
        "progress": {
            "completed": [
                "Каталог 31 744 територіальних записів КАТОТТГ",
                "Класифікація дев'яти типів територій",
                "Пошук та адміністративна ієрархія",
                "24 обласні ради з кодами ЄДРПОУ",
                "Окремі MCP для територій України",
            ],
            "in_progress": [
                "Співставлення територіальних громад із радами та ЄДРПОУ",
                "Розвиток системи зворотного зв'язку",
            ],
            "planned": [
                "Рішення органів місцевого самоврядування",
                "Публічні закупівлі та бюджети",
                "Декларації та інші перевірені відкриті дані",
            ],
        },
        "feedback": {
            "message": (
                "Ми готуємо можливість повідомляти про помилки, "
                "пропонувати джерела та нові функції."
            ),
            "status": "planned",
            "accepting_submissions": False,
        },
        "data_notice": (
            "Не всі заплановані джерела вже підключені. "
            "Перевіряйте джерело та дату актуальності "
            "кожного набору даних."
        ),
    }

    if record is not None:
        result["territory"] = {
            "code": record["code"],
            "name": record["name"],
            **get_territory_type(record),
        }
        result["welcome"] = (
            f'Вітаємо в MCP території «{record["name"]}»! 🇺🇦 '
            "Тут можна отримати її офіційні дані "
            "та інформацію про розвиток проєкту."
        )

    return result


def submit_feedback_data(
    feedback_type: str,
    message: str,
    territory_code: str = "",
    source_url: str = "",
) -> dict:
    """Прийняти відгук без зміни офіційних реєстрів."""
    import hashlib
    import sqlite3
    from pathlib import Path
    from urllib.parse import urlsplit

    from national_mcp import BY_CODE

    db = Path(__file__).resolve().parents[1] / "data/feedback/feedback.db"

    if feedback_type not in {"error", "source", "idea", "other"}:
        return {"accepted": False, "error": "Невідомий тип звернення"}

    if not isinstance(message, str):
        return {"accepted": False, "error": "Повідомлення має бути текстом"}

    message = message.strip()

    if not 10 <= len(message) <= 2000:
        return {
            "accepted": False,
            "error": "Довжина повідомлення: від 10 до 2000 символів",
        }

    territory_code = (territory_code or "").strip().upper()

    if territory_code and territory_code not in BY_CODE:
        return {"accepted": False, "error": "Невідомий код КАТОТТГ"}

    source_url = (source_url or "").strip()

    if len(source_url) > 500:
        return {"accepted": False, "error": "Посилання занадто довге"}

    if source_url:
        parsed = urlsplit(source_url)
        if (
            parsed.scheme not in {"http", "https"}
            or not parsed.hostname
            or parsed.username is not None
            or parsed.password is not None
        ):
            return {"accepted": False, "error": "Некоректне HTTP/HTTPS-посилання"}

    fingerprint = "\n".join([
        feedback_type,
        territory_code,
        message.casefold(),
        source_url,
    ])

    message_hash = hashlib.sha256(
        fingerprint.encode("utf-8")
    ).hexdigest()

    try:
        with sqlite3.connect(str(db), timeout=5) as conn:
            conn.execute("BEGIN IMMEDIATE")

            duplicate = conn.execute("""
                SELECT id FROM feedback
                WHERE message_hash = ?
                  AND created_at >= datetime('now', '-1 hour')
                LIMIT 1
            """, (message_hash,)).fetchone()

            if duplicate:
                return {
                    "accepted": False,
                    "duplicate": True,
                    "feedback_id": duplicate[0],
                    "message": "Таке звернення вже отримано",
                }

            recent_count = conn.execute("""
                SELECT COUNT(*) FROM feedback
                WHERE created_at >= datetime('now', '-1 hour')
            """).fetchone()[0]

            if recent_count >= 100:
                return {
                    "accepted": False,
                    "error": "Тимчасово досягнуто ліміту звернень",
                }

            cursor = conn.execute("""
                INSERT INTO feedback (
                    feedback_type,
                    territory_code,
                    message,
                    source_url,
                    message_hash
                ) VALUES (?, ?, ?, ?, ?)
            """, (
                feedback_type,
                territory_code or None,
                message,
                source_url or None,
                message_hash,
            ))

            feedback_id = cursor.lastrowid

        return {
            "accepted": True,
            "feedback_id": feedback_id,
            "status": "new",
            "message": "Дякуємо! Ваше звернення збережено для розгляду.",
        }

    except sqlite3.Error:
        return {
            "accepted": False,
            "error": "Тимчасова помилка збереження звернення",
        }
