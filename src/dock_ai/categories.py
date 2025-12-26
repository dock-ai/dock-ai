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
