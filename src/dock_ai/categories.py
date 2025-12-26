"""Business categories and their available filters."""

from enum import Enum


class Category(str, Enum):
    """Supported business categories."""
    RESTAURANT = "restaurant"
    HAIR_SALON = "hair_salon"
    SPA = "spa"
    FITNESS = "fitness"


# Filters available for each category
CATEGORY_FILTERS = {
    Category.RESTAURANT: {
        "cuisine": [
            "French", "Japanese", "Italian", "Indian", "American",
            "Chinese", "Mexican", "Thai", "Mediterranean", "Korean"
        ],
        "price_range": ["$", "$$", "$$$", "$$$$"],
        "ambiance": ["Casual", "Fine Dining", "Family", "Romantic", "Business"],
    },
    Category.HAIR_SALON: {
        "service": [
            "Haircut", "Coloring", "Balayage", "Highlights",
            "Treatment", "Styling", "Blow Dry"
        ],
        "gender": ["Men", "Women", "Unisex"],
    },
    Category.SPA: {
        "service": [
            "Massage", "Facial", "Body Treatment",
            "Manicure", "Pedicure", "Waxing"
        ],
        "duration": ["30min", "60min", "90min", "120min"],
    },
    Category.FITNESS: {
        "activity": [
            "Gym", "Yoga", "Pilates", "CrossFit",
            "Swimming", "Tennis", "Boxing", "Dance"
        ],
        "level": ["Beginner", "Intermediate", "Advanced"],
    },
}


def get_filters_for_category(category: str) -> dict:
    """
    Get available filters for a category.

    Args:
        category: Category name (case-insensitive)

    Returns:
        Dictionary of filter names and their possible values
    """
    category_lower = category.lower().replace(" ", "_")

    try:
        cat_enum = Category(category_lower)
        return CATEGORY_FILTERS.get(cat_enum, {})
    except ValueError:
        return {}


def get_available_categories() -> list[str]:
    """Get list of all available category names."""
    return [c.value for c in Category]
