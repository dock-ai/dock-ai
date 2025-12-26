"""Business categories and their available filters per tool."""

from enum import Enum


class Category(str, Enum):
    """Supported business categories."""
    RESTAURANT = "restaurant"
    HAIR_SALON = "hair_salon"
    SPA = "spa"
    FITNESS = "fitness"


class Tool(str, Enum):
    """Tools that support category-specific filters."""
    SEARCH = "search"
    CHECK_AVAILABILITY = "check_availability"
    BOOK = "book"


# Filters available for each category and tool
CATEGORY_TOOL_FILTERS = {
    Category.RESTAURANT: {
        Tool.SEARCH: {
            "cuisine": [
                "French", "Japanese", "Italian", "Indian", "American",
                "Chinese", "Mexican", "Thai", "Mediterranean", "Korean"
            ],
            "price_range": ["$", "$$", "$$$", "$$$$"],
            "ambiance": ["Casual", "Fine Dining", "Family", "Romantic", "Business"],
        },
        Tool.CHECK_AVAILABILITY: {
            "party_size": {"type": "integer", "min": 1, "max": 20, "required": True},
            "date": {"type": "date", "format": "YYYY-MM-DD", "required": True},
        },
        Tool.BOOK: {
            "party_size": {"type": "integer", "min": 1, "max": 20, "required": True},
            "date": {"type": "date", "format": "YYYY-MM-DD", "required": True},
            "time": {"type": "time", "format": "HH:MM", "required": True},
        },
    },
    Category.HAIR_SALON: {
        Tool.SEARCH: {
            "service": [
                "Haircut", "Coloring", "Balayage", "Highlights",
                "Treatment", "Styling", "Blow Dry"
            ],
            "gender": ["Men", "Women", "Unisex"],
        },
        Tool.CHECK_AVAILABILITY: {
            "service": {"type": "string", "required": True},
            "date": {"type": "date", "format": "YYYY-MM-DD", "required": True},
        },
        Tool.BOOK: {
            "service": {"type": "string", "required": True},
            "date": {"type": "date", "format": "YYYY-MM-DD", "required": True},
            "time": {"type": "time", "format": "HH:MM", "required": True},
            "duration": {"type": "string", "options": ["30min", "60min", "90min"], "required": False},
        },
    },
    Category.SPA: {
        Tool.SEARCH: {
            "service": [
                "Massage", "Facial", "Body Treatment",
                "Manicure", "Pedicure", "Waxing"
            ],
        },
        Tool.CHECK_AVAILABILITY: {
            "service": {"type": "string", "required": True},
            "date": {"type": "date", "format": "YYYY-MM-DD", "required": True},
            "duration": {"type": "string", "options": ["30min", "60min", "90min", "120min"], "required": False},
        },
        Tool.BOOK: {
            "service": {"type": "string", "required": True},
            "date": {"type": "date", "format": "YYYY-MM-DD", "required": True},
            "time": {"type": "time", "format": "HH:MM", "required": True},
            "duration": {"type": "string", "options": ["30min", "60min", "90min", "120min"], "required": True},
        },
    },
    Category.FITNESS: {
        Tool.SEARCH: {
            "activity": [
                "Gym", "Yoga", "Pilates", "CrossFit",
                "Swimming", "Tennis", "Boxing", "Dance"
            ],
            "level": ["Beginner", "Intermediate", "Advanced"],
        },
        Tool.CHECK_AVAILABILITY: {
            "activity": {"type": "string", "required": True},
            "date": {"type": "date", "format": "YYYY-MM-DD", "required": True},
        },
        Tool.BOOK: {
            "activity": {"type": "string", "required": True},
            "date": {"type": "date", "format": "YYYY-MM-DD", "required": True},
            "time": {"type": "time", "format": "HH:MM", "required": True},
        },
    },
}


def get_filters_for_category(category: str, tool: str = "search") -> dict:
    """
    Get available filters for a category and tool.

    Args:
        category: Category name (case-insensitive)
        tool: Tool name (search, check_availability, book)

    Returns:
        Dictionary of filter names and their possible values or schema
    """
    category_lower = category.lower().replace(" ", "_")
    tool_lower = tool.lower()

    try:
        cat_enum = Category(category_lower)
        tool_enum = Tool(tool_lower)
        category_filters = CATEGORY_TOOL_FILTERS.get(cat_enum, {})
        return category_filters.get(tool_enum, {})
    except ValueError:
        return {}


def get_available_categories() -> list[str]:
    """Get list of all available category names."""
    return [c.value for c in Category]


def get_available_tools() -> list[str]:
    """Get list of all available tool names."""
    return [t.value for t in Tool]


def validate_params(category: str, tool: str, params: dict) -> tuple[bool, str | None]:
    """
    Validate params against the expected schema for a category and tool.

    Args:
        category: Category name
        tool: Tool name (check_availability, book)
        params: Parameters to validate

    Returns:
        Tuple of (is_valid, error_message)
    """
    filters = get_filters_for_category(category, tool)
    if not filters:
        return False, f"Unknown category '{category}' or tool '{tool}'"

    missing = []
    invalid = []

    for param_name, schema in filters.items():
        if isinstance(schema, dict):  # It's a schema definition
            is_required = schema.get("required", False)
            param_type = schema.get("type")

            if param_name not in params:
                if is_required:
                    missing.append(param_name)
                continue

            value = params[param_name]

            # Type validation
            if param_type == "integer":
                if not isinstance(value, int):
                    invalid.append(f"{param_name} must be an integer")
                else:
                    min_val = schema.get("min")
                    max_val = schema.get("max")
                    if min_val is not None and value < min_val:
                        invalid.append(f"{param_name} must be >= {min_val}")
                    if max_val is not None and value > max_val:
                        invalid.append(f"{param_name} must be <= {max_val}")

            elif param_type == "date":
                if not isinstance(value, str):
                    invalid.append(f"{param_name} must be a string in YYYY-MM-DD format")
                # Basic date format check
                elif len(value) != 10 or value[4] != "-" or value[7] != "-":
                    invalid.append(f"{param_name} must be in YYYY-MM-DD format")

            elif param_type == "time":
                if not isinstance(value, str):
                    invalid.append(f"{param_name} must be a string in HH:MM format")
                elif len(value) != 5 or value[2] != ":":
                    invalid.append(f"{param_name} must be in HH:MM format")

            elif param_type == "string":
                if not isinstance(value, str):
                    invalid.append(f"{param_name} must be a string")
                options = schema.get("options")
                if options and value not in options:
                    invalid.append(f"{param_name} must be one of: {', '.join(options)}")

    if missing:
        return False, f"Missing required parameters: {', '.join(missing)}"
    if invalid:
        return False, "; ".join(invalid)

    return True, None


def is_valid_category(category: str) -> bool:
    """Check if a category is valid."""
    try:
        Category(category.lower().replace(" ", "_"))
        return True
    except ValueError:
        return False
