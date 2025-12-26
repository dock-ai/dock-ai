"""Tests for the categories module."""

import pytest

from dock_ai.categories import (
    Category,
    Tool,
    get_filters_for_category,
    get_available_categories,
    get_available_tools,
    validate_params,
    is_valid_category,
)


class TestCategory:
    """Test Category enum."""

    def test_all_categories_exist(self):
        """Verify all expected categories are defined."""
        expected = ["restaurant", "hair_salon", "spa", "fitness"]
        actual = [c.value for c in Category]
        assert sorted(actual) == sorted(expected)


class TestTool:
    """Test Tool enum."""

    def test_all_tools_exist(self):
        """Verify all expected tools are defined."""
        expected = ["search", "check_availability", "book"]
        actual = [t.value for t in Tool]
        assert sorted(actual) == sorted(expected)


class TestGetFiltersForCategory:
    """Test get_filters_for_category function."""

    def test_restaurant_search_filters(self):
        """Get search filters for restaurants."""
        filters = get_filters_for_category("restaurant", "search")
        assert "cuisine" in filters
        assert "price_range" in filters
        assert isinstance(filters["cuisine"], list)

    def test_restaurant_book_filters(self):
        """Get book filters for restaurants."""
        filters = get_filters_for_category("restaurant", "book")
        assert "party_size" in filters
        assert "date" in filters
        assert "time" in filters
        assert filters["party_size"]["required"] is True

    def test_hair_salon_book_filters(self):
        """Get book filters for hair salons (no party_size)."""
        filters = get_filters_for_category("hair_salon", "book")
        assert "service" in filters
        assert "date" in filters
        assert "party_size" not in filters

    def test_unknown_category(self):
        """Unknown category returns empty dict."""
        filters = get_filters_for_category("unknown_category", "search")
        assert filters == {}

    def test_case_insensitive(self):
        """Category lookup is case-insensitive."""
        filters = get_filters_for_category("RESTAURANT", "search")
        assert "cuisine" in filters


class TestValidateParams:
    """Test validate_params function."""

    def test_valid_restaurant_book_params(self):
        """Valid restaurant booking params pass validation."""
        params = {"date": "2025-01-15", "time": "19:30", "party_size": 4}
        is_valid, error = validate_params("restaurant", "book", params)
        assert is_valid is True
        assert error is None

    def test_missing_required_param(self):
        """Missing required param fails validation."""
        params = {"date": "2025-01-15", "time": "19:30"}  # missing party_size
        is_valid, error = validate_params("restaurant", "book", params)
        assert is_valid is False
        assert "party_size" in error

    def test_invalid_party_size_type(self):
        """Invalid party_size type fails validation."""
        params = {"date": "2025-01-15", "time": "19:30", "party_size": "four"}
        is_valid, error = validate_params("restaurant", "book", params)
        assert is_valid is False
        assert "integer" in error

    def test_party_size_out_of_range(self):
        """Party size out of range fails validation."""
        params = {"date": "2025-01-15", "time": "19:30", "party_size": 100}
        is_valid, error = validate_params("restaurant", "book", params)
        assert is_valid is False
        assert "<=" in error

    def test_invalid_date_format(self):
        """Invalid date format fails validation."""
        params = {"date": "15-01-2025", "time": "19:30", "party_size": 4}
        is_valid, error = validate_params("restaurant", "book", params)
        assert is_valid is False
        assert "YYYY-MM-DD" in error

    def test_invalid_time_format(self):
        """Invalid time format fails validation."""
        params = {"date": "2025-01-15", "time": "7:30pm", "party_size": 4}
        is_valid, error = validate_params("restaurant", "book", params)
        assert is_valid is False
        assert "HH:MM" in error

    def test_hair_salon_valid_params(self):
        """Valid hair salon params pass validation."""
        params = {"date": "2025-01-15", "time": "14:00", "service": "Haircut"}
        is_valid, error = validate_params("hair_salon", "book", params)
        assert is_valid is True

    def test_unknown_category_validation(self):
        """Unknown category fails validation."""
        params = {"date": "2025-01-15"}
        is_valid, error = validate_params("unknown", "book", params)
        assert is_valid is False
        assert "Unknown" in error


class TestIsValidCategory:
    """Test is_valid_category function."""

    def test_valid_categories(self):
        """Valid categories return True."""
        assert is_valid_category("restaurant") is True
        assert is_valid_category("hair_salon") is True
        assert is_valid_category("spa") is True
        assert is_valid_category("fitness") is True

    def test_case_insensitive(self):
        """Category check is case-insensitive."""
        assert is_valid_category("RESTAURANT") is True
        assert is_valid_category("Hair_Salon") is True

    def test_invalid_category(self):
        """Invalid categories return False."""
        assert is_valid_category("bar") is False
        assert is_valid_category("") is False
        assert is_valid_category("restaurant ") is False


class TestGetAvailable:
    """Test list functions."""

    def test_get_available_categories(self):
        """Get all available category names."""
        categories = get_available_categories()
        assert "restaurant" in categories
        assert "hair_salon" in categories
        assert len(categories) == 4

    def test_get_available_tools(self):
        """Get all available tool names."""
        tools = get_available_tools()
        assert "search" in tools
        assert "book" in tools
        assert "check_availability" in tools
