"""Універсальні MCP-інструменти наборів даних."""

from dataset_manager.manager import list_datasets as get_registered_datasets


def list_datasets() -> dict:
    """Повернути перелік публічно доступних наборів даних."""
    datasets = []

    for dataset in get_registered_datasets():
        if (
            dataset["status"] != "active"
            or dataset["is_published"] != 1
        ):
            continue

        datasets.append({
            "id": dataset["id"],
            "name": dataset["name"],
            "description": dataset["description"],
        })

    return {
        "total": len(datasets),
        "datasets": datasets,
    }


def describe_dataset(dataset_id: str) -> dict:
    """Повернути опис лише публічно доступного НД."""
    from dataset_manager.manager import get_dataset, list_fields

    dataset = get_dataset(dataset_id)

    if (
        dataset is None
        or dataset["status"] != "active"
        or dataset["is_published"] != 1
    ):
        return {"error": "Набір даних недоступний"}

    fields = list_fields(dataset_id)

    return {
        "id": dataset["id"],
        "name": dataset["name"],
        "description": dataset["description"],
        "fields": [
            {
                "key": field["field_key"],
                "name": field["field_name"],
                "type": field["field_type"],
                "required": bool(field["required"]),
            }
            for field in fields
        ],
    }
