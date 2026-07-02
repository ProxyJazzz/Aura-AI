def format_list_to_string(items: list) -> str:
    """Format a list to a comma separated string safely."""
    if not items:
        return ""
    return ",".join(items)

def parse_string_to_list(item_str: str) -> list:
    """Parse a comma separated string back to a list."""
    if not item_str:
        return []
    return [i.strip() for i in item_str.split(",") if i.strip()]
