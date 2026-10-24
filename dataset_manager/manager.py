"""Локальний менеджер наборів даних України."""

import sqlite3
from pathlib import Path

DB_PATH = Path(__file__).resolve().parent / "datasets.db"

STATUSES = {"draft", "active", "disabled", "archived"}


def get_connection():
    return sqlite3.connect(DB_PATH)


def list_datasets():
    with get_connection() as conn:
        conn.row_factory = sqlite3.Row
        rows = conn.execute(
            "SELECT * FROM datasets ORDER BY name"
        ).fetchall()
        return [dict(row) for row in rows]


def get_dataset(dataset_id):
    with get_connection() as conn:
        conn.row_factory = sqlite3.Row
        row = conn.execute(
            "SELECT * FROM datasets WHERE id = ?",
            (dataset_id,)
        ).fetchone()
        return dict(row) if row else None


def set_dataset_status(dataset_id, status):
    if status not in STATUSES:
        raise ValueError(f"Невідомий статус: {status}")

    with get_connection() as conn:
        cursor = conn.execute(
            """
            UPDATE datasets
            SET status = ?, updated_at = CURRENT_TIMESTAMP
            WHERE id = ?
            """,
            (status, dataset_id)
        )
        if cursor.rowcount != 1:
            raise ValueError(f"НД не знайдено: {dataset_id}")
        conn.commit()

    return get_dataset(dataset_id)


def get_active_datasets():
    return [
        dataset for dataset in list_datasets()
        if dataset["status"] == "active"
    ]


def create_dataset(dataset_id, name, description="", source_path=None):
    """Зареєструвати новий НД без зміни його вихідних даних."""
    import re

    if not isinstance(dataset_id, str) or not re.fullmatch(
        r"[a-z][a-z0-9_]{2,63}", dataset_id
    ):
        raise ValueError("ID: 3–64 символи, латиниця, цифри та _")

    if not isinstance(name, str) or not 3 <= len(name.strip()) <= 200:
        raise ValueError("Назва НД повинна містити 3–200 символів")

    if not isinstance(description, str) or len(description) > 2000:
        raise ValueError("Некоректний опис НД")

    if source_path is not None:
        if not isinstance(source_path, str):
            raise ValueError("Шлях до джерела має бути текстом")
        source = Path(source_path).resolve(strict=True)
        official_root = (
            DB_PATH.parent.parent / "data" / "official"
        ).resolve()

        if not source.is_file() or not source.is_relative_to(official_root):
            raise ValueError("Джерело має бути файлом у data/official")

        source_path = str(source)

    with get_connection() as conn:
        try:
            conn.execute(
                """
                INSERT INTO datasets
                (id, name, description, source_path, status)
                VALUES (?, ?, ?, ?, 'draft')
                """,
                (
                    dataset_id,
                    name.strip(),
                    description.strip(),
                    source_path,
                ),
            )
            conn.commit()
        except sqlite3.IntegrityError:
            raise ValueError(f"НД уже існує: {dataset_id}")

    return get_dataset(dataset_id)


FIELD_TYPES = {
    "text", "integer", "decimal",
    "boolean", "date", "url", "json"
}


def add_field(dataset_id, field_key, field_name,
              field_type="text", required=False):
    """Додати параметр до наявного набору даних."""
    import re

    if get_dataset(dataset_id) is None:
        raise ValueError(f"НД не знайдено: {dataset_id}")

    if not isinstance(field_key, str) or not re.fullmatch(
        r"[a-z][a-z0-9_]{1,63}", field_key
    ):
        raise ValueError("Некоректний ідентифікатор параметра")

    if not isinstance(field_name, str) or not 2 <= len(field_name.strip()) <= 200:
        raise ValueError("Назва параметра: від 2 до 200 символів")

    if field_type not in FIELD_TYPES:
        raise ValueError(f"Невідомий тип параметра: {field_type}")

    if not isinstance(required, bool):
        raise ValueError("required має бути True або False")

    with get_connection() as conn:
        try:
            conn.execute(
                """
                INSERT INTO dataset_fields
                (dataset_id, field_key, field_name, field_type, required)
                VALUES (?, ?, ?, ?, ?)
                """,
                (
                    dataset_id,
                    field_key,
                    field_name.strip(),
                    field_type,
                    int(required),
                )
            )
            conn.commit()
        except sqlite3.IntegrityError as exc:
            raise ValueError(
                f"Параметр уже існує або не може бути доданий: {field_key}"
            ) from exc

    return {
        "dataset_id": dataset_id,
        "field_key": field_key,
        "field_name": field_name.strip(),
        "field_type": field_type,
        "required": required,
    }


def list_fields(dataset_id, include_inactive=False):
    """Повернути параметри заданого НД."""
    if get_dataset(dataset_id) is None:
        raise ValueError(f"НД не знайдено: {dataset_id}")

    if not isinstance(include_inactive, bool):
        raise ValueError("include_inactive має бути True або False")

    with get_connection() as conn:
        conn.row_factory = sqlite3.Row
        sql = """
            SELECT id, dataset_id, field_key, field_name,
                   field_type, required, is_active, created_at
            FROM dataset_fields
            WHERE dataset_id = ?
        """
        if not include_inactive:
            sql += " AND is_active = 1"

        sql += " ORDER BY id"

        rows = conn.execute(sql, (dataset_id,)).fetchall()
        return [dict(row) for row in rows]


def update_field(dataset_id, field_key, *, field_name=None, required=None):
    """Змінити назву або обов'язковість параметра."""
    if get_dataset(dataset_id) is None:
        raise ValueError(f"НД не знайдено: {dataset_id}")

    if field_name is None and required is None:
        raise ValueError("Не вказано змін")

    if field_name is not None:
        if not isinstance(field_name, str) or not 2 <= len(field_name.strip()) <= 200:
            raise ValueError("Некоректна назва параметра")

    if required is not None and not isinstance(required, bool):
        raise ValueError("required має бути True або False")

    changes = []
    values = []

    if field_name is not None:
        changes.append("field_name = ?")
        values.append(field_name.strip())

    if required is not None:
        changes.append("required = ?")
        values.append(int(required))

    values.extend([dataset_id, field_key])

    with get_connection() as conn:
        cursor = conn.execute(
            f"UPDATE dataset_fields SET {', '.join(changes)} "
            "WHERE dataset_id = ? AND field_key = ?",
            values
        )
        if cursor.rowcount != 1:
            raise ValueError(f"Параметр не знайдено: {field_key}")
        conn.commit()

    return next(
        f for f in list_fields(dataset_id, include_inactive=True)
        if f["field_key"] == field_key
    )


def set_field_active(dataset_id, field_key, active):
    """Увімкнути або вимкнути параметр без видалення."""
    if not isinstance(active, bool):
        raise ValueError("active має бути True або False")

    if get_dataset(dataset_id) is None:
        raise ValueError(f"НД не знайдено: {dataset_id}")

    with get_connection() as conn:
        cursor = conn.execute(
            """
            UPDATE dataset_fields
            SET is_active = ?
            WHERE dataset_id = ? AND field_key = ?
            """,
            (int(active), dataset_id, field_key)
        )
        if cursor.rowcount != 1:
            raise ValueError(f"Параметр не знайдено: {field_key}")
        conn.commit()

    return next(
        f for f in list_fields(dataset_id, include_inactive=True)
        if f["field_key"] == field_key
    )


def create_record(dataset_id, record_key):
    """Створити запис усередині конкретного НД."""
    import re

    if get_dataset(dataset_id) is None:
        raise ValueError(f"НД не знайдено: {dataset_id}")

    if not isinstance(record_key, str) or not re.fullmatch(
        r"[A-Za-z0-9][A-Za-z0-9_-]{0,127}", record_key
    ):
        raise ValueError("Некоректний ідентифікатор запису")

    with get_connection() as conn:
        conn.execute("PRAGMA foreign_keys = ON")
        try:
            cursor = conn.execute(
                """
                INSERT INTO dataset_records (dataset_id, record_key)
                VALUES (?, ?)
                """,
                (dataset_id, record_key)
            )
            conn.commit()
        except sqlite3.IntegrityError as exc:
            raise ValueError(
                f"Запис уже існує: {record_key}"
            ) from exc

        return {
            "id": cursor.lastrowid,
            "dataset_id": dataset_id,
            "record_key": record_key,
        }


def set_field_value(dataset_id, record_key, field_key, value):
    """Зберегти значення параметра з перевіркою типу та належності до НД."""
    import json
    import math
    from datetime import date
    from decimal import Decimal, InvalidOperation
    from urllib.parse import urlsplit

    with get_connection() as conn:
        conn.execute("PRAGMA foreign_keys = ON")

        record = conn.execute(
            """
            SELECT id FROM dataset_records
            WHERE dataset_id = ? AND record_key = ?
            """,
            (dataset_id, record_key)
        ).fetchone()

        if record is None:
            raise ValueError("Запис не знайдено")

        field = conn.execute(
            """
            SELECT id, field_type, is_active
            FROM dataset_fields
            WHERE dataset_id = ? AND field_key = ?
            """,
            (dataset_id, field_key)
        ).fetchone()

        if field is None or field[2] != 1:
            raise ValueError("Параметр не знайдено або вимкнений")

        field_id, field_type, _ = field

        if field_type == "text":
            if not isinstance(value, str):
                raise ValueError("Очікується текст")

        elif field_type == "integer":
            if type(value) is not int:
                raise ValueError("Очікується ціле число")

        elif field_type == "decimal":
            if isinstance(value, bool) or not isinstance(
                value, (int, float, str)
            ):
                raise ValueError("Очікується десяткове число")
            try:
                number = Decimal(str(value))
            except InvalidOperation as exc:
                raise ValueError("Некоректне десяткове число") from exc
            if not number.is_finite():
                raise ValueError("Число має бути скінченним")
            value = str(number)

        elif field_type == "boolean":
            if type(value) is not bool:
                raise ValueError("Очікується True або False")

        elif field_type == "date":
            if not isinstance(value, str):
                raise ValueError("Очікується дата YYYY-MM-DD")
            try:
                if date.fromisoformat(value).isoformat() != value:
                    raise ValueError("Некоректний формат дати")
            except ValueError as exc:
                raise ValueError("Некоректна дата") from exc

        elif field_type == "url":
            if not isinstance(value, str):
                raise ValueError("Очікується URL")
            url = urlsplit(value)
            if (
                url.scheme not in ("http", "https")
                or not url.hostname
                or url.username is not None
                or url.password is not None
            ):
                raise ValueError("Некоректна вебадреса")

        elif field_type == "json":
            try:
                json.dumps(value, allow_nan=False)
            except (TypeError, ValueError) as exc:
                raise ValueError("Значення не є коректним JSON") from exc

        else:
            raise ValueError("Невідомий тип параметра")

        serialized = json.dumps(value, ensure_ascii=False, allow_nan=False)

        conn.execute(
            """
            INSERT INTO dataset_values (record_id, field_id, value_json)
            VALUES (?, ?, ?)
            ON CONFLICT(record_id, field_id)
            DO UPDATE SET
                value_json = excluded.value_json,
                updated_at = CURRENT_TIMESTAMP
            """,
            (record[0], field_id, serialized)
        )
        conn.commit()

    return {
        "dataset_id": dataset_id,
        "record_key": record_key,
        "field_key": field_key,
        "value": value,
    }


def get_record(dataset_id, record_key, include_inactive=False):
    """Отримати запис НД разом зі значеннями його параметрів."""
    import json

    if not isinstance(include_inactive, bool):
        raise ValueError("include_inactive має бути True або False")

    with get_connection() as conn:
        conn.row_factory = sqlite3.Row

        record = conn.execute(
            """
            SELECT id, dataset_id, record_key, created_at, updated_at
            FROM dataset_records
            WHERE dataset_id = ? AND record_key = ?
            """,
            (dataset_id, record_key)
        ).fetchone()

        if record is None:
            return None

        sql = """
            SELECT f.field_key, f.field_name, f.field_type,
                   f.is_active, v.value_json
            FROM dataset_values AS v
            JOIN dataset_fields AS f ON f.id = v.field_id
            WHERE v.record_id = ? AND f.dataset_id = ?
        """

        if not include_inactive:
            sql += " AND f.is_active = 1"

        sql += " ORDER BY f.id"

        rows = conn.execute(
            sql, (record["id"], dataset_id)
        ).fetchall()

        values = {
            row["field_key"]: json.loads(row["value_json"])
            for row in rows
        }

        return {
            "id": record["id"],
            "dataset_id": record["dataset_id"],
            "record_key": record["record_key"],
            "values": values,
            "created_at": record["created_at"],
            "updated_at": record["updated_at"],
        }
