def get_model_custom_fields(model_data: dict) -> dict:
    fields = model_data.get("custom_fields_values", [])
    fields = fields if fields else []

    custom_fields = {}

    for field in fields:
        filed_id = field["field_id"]
        field_values = field["values"]
        field_type = field["field_type"]

        if field_type == "multiselect":
            field_values = [value["value"] for value in field_values]
        else:
            field_values = field["values"][0]["value"]

        custom_fields.setdefault(filed_id, field_values)

    return custom_fields
