"""Tests for the server module."""

import pytest
from fastmcp.exceptions import ToolError

from dock_ai.server import (
    get_filters,
    search_venues,
    check_availability,
    book,
    cancel,
    list_venues,
    get_venue_details,
    get_booking_status,
    find_venue_by_domain,
    booking_manager,
)


# Access the underlying functions from the FunctionTool wrappers
_get_filters = get_filters.fn
_search_venues = search_venues.fn
_check_availability = check_availability.fn
_book = book.fn
_cancel = cancel.fn
_list_venues = list_venues.fn
_get_venue_details = get_venue_details.fn
_get_booking_status = get_booking_status.fn
_find_venue_by_domain = find_venue_by_domain.fn


class TestGetFilters:
    """Test get_filters tool."""

    @pytest.mark.asyncio
    async def test_valid_category_and_tool(self):
        """Valid category and tool returns filters."""
        result = await _get_filters("restaurant", "search")
        assert result["category"] == "restaurant"
        assert result["tool"] == "search"
        assert "cuisine" in result["parameters"]

    @pytest.mark.asyncio
    async def test_invalid_category_raises_error(self):
        """Invalid category raises ToolError."""
        with pytest.raises(ToolError) as exc_info:
            await _get_filters("invalid", "search")
        assert "Unknown category" in str(exc_info.value)

    @pytest.mark.asyncio
    async def test_invalid_tool_raises_error(self):
        """Invalid tool raises ToolError."""
        with pytest.raises(ToolError) as exc_info:
            await _get_filters("restaurant", "invalid_tool")
        assert "Unknown category" in str(exc_info.value)


class TestSearchVenues:
    """Test search_venues tool."""

    @pytest.mark.asyncio
    async def test_valid_search(self):
        """Valid search returns venues."""
        result = await _search_venues(
            category="restaurant",
            city="Paris",
            date="2025-01-15",
            party_size=4
        )
        assert "venues" in result
        assert "count" in result
        assert result["count"] >= 0

    @pytest.mark.asyncio
    async def test_invalid_category_raises_error(self):
        """Invalid category raises ToolError."""
        with pytest.raises(ToolError) as exc_info:
            await _search_venues(
                category="invalid",
                city="Paris",
                date="2025-01-15",
                party_size=4
            )
        assert "Invalid category" in str(exc_info.value)

    @pytest.mark.asyncio
    async def test_empty_city_raises_error(self):
        """Empty city raises ToolError."""
        with pytest.raises(ToolError) as exc_info:
            await _search_venues(
                category="restaurant",
                city="",
                date="2025-01-15",
                party_size=4
            )
        assert "city is required" in str(exc_info.value)

    @pytest.mark.asyncio
    async def test_invalid_date_raises_error(self):
        """Invalid date format raises ToolError."""
        with pytest.raises(ToolError) as exc_info:
            await _search_venues(
                category="restaurant",
                city="Paris",
                date="Jan 15",  # Wrong format (not 10 chars)
                party_size=4
            )
        assert "YYYY-MM-DD" in str(exc_info.value)

    @pytest.mark.asyncio
    async def test_invalid_party_size_raises_error(self):
        """Invalid party_size raises ToolError."""
        with pytest.raises(ToolError) as exc_info:
            await _search_venues(
                category="restaurant",
                city="Paris",
                date="2025-01-15",
                party_size=0
            )
        assert "positive integer" in str(exc_info.value)


class TestCheckAvailability:
    """Test check_availability tool."""

    @pytest.mark.asyncio
    async def test_valid_check(self):
        """Valid check returns slots."""
        result = await _check_availability(
            venue_id="demo_paris_001",
            category="restaurant",
            params={"date": "2025-01-15", "party_size": 4}
        )
        assert "slots" in result
        assert len(result["slots"]) > 0

    @pytest.mark.asyncio
    async def test_invalid_category_raises_error(self):
        """Invalid category raises ToolError."""
        with pytest.raises(ToolError) as exc_info:
            await _check_availability(
                venue_id="demo_paris_001",
                category="invalid",
                params={"date": "2025-01-15", "party_size": 4}
            )
        assert "Invalid category" in str(exc_info.value)

    @pytest.mark.asyncio
    async def test_missing_params_raises_error(self):
        """Missing required params raises ToolError."""
        with pytest.raises(ToolError) as exc_info:
            await _check_availability(
                venue_id="demo_paris_001",
                category="restaurant",
                params={"date": "2025-01-15"}  # Missing party_size
            )
        assert "party_size" in str(exc_info.value)


class TestBook:
    """Test book tool."""

    @pytest.mark.asyncio
    async def test_valid_booking(self):
        """Valid booking returns confirmation."""
        result = await _book(
            venue_id="demo_paris_001",
            category="restaurant",
            params={"date": "2025-01-15", "time": "19:30", "party_size": 4},
            customer_name="John Doe",
            customer_email="john@example.com",
            customer_phone="+33612345678"
        )
        assert "id" in result
        assert result["status"] == "confirmed"
        assert "booking_" in result["id"]

    @pytest.mark.asyncio
    async def test_invalid_category_raises_error(self):
        """Invalid category raises ToolError."""
        with pytest.raises(ToolError) as exc_info:
            await _book(
                venue_id="demo_paris_001",
                category="invalid",
                params={"date": "2025-01-15", "time": "19:30", "party_size": 4},
                customer_name="John Doe",
                customer_email="john@example.com",
                customer_phone="+33612345678"
            )
        assert "Invalid category" in str(exc_info.value)

    @pytest.mark.asyncio
    async def test_missing_customer_name_raises_error(self):
        """Missing customer name raises ToolError."""
        with pytest.raises(ToolError) as exc_info:
            await _book(
                venue_id="demo_paris_001",
                category="restaurant",
                params={"date": "2025-01-15", "time": "19:30", "party_size": 4},
                customer_name="",
                customer_email="john@example.com",
                customer_phone="+33612345678"
            )
        assert "customer_name is required" in str(exc_info.value)

    @pytest.mark.asyncio
    async def test_invalid_email_raises_error(self):
        """Invalid email raises ToolError."""
        with pytest.raises(ToolError) as exc_info:
            await _book(
                venue_id="demo_paris_001",
                category="restaurant",
                params={"date": "2025-01-15", "time": "19:30", "party_size": 4},
                customer_name="John Doe",
                customer_email="invalid-email",
                customer_phone="+33612345678"
            )
        assert "Valid customer_email" in str(exc_info.value)


class TestListVenues:
    """Test list_venues tool."""

    @pytest.mark.asyncio
    async def test_invalid_category_raises_error(self):
        """Invalid category raises ToolError."""
        with pytest.raises(ToolError) as exc_info:
            await _list_venues(category="invalid")
        assert "Invalid category" in str(exc_info.value)


class TestBookingManager:
    """Test BookingManager functionality."""

    def test_generate_booking_id(self):
        """Generated booking ID has correct format."""
        booking_id = booking_manager.generate_booking_id()
        assert booking_id.startswith("booking_")
        assert len(booking_id) == 20  # "booking_" + 12 hex chars

    @pytest.mark.asyncio
    async def test_check_slot_available(self):
        """Slot availability check works."""
        # Should return True for demo (no real DB check)
        result = await booking_manager.check_slot_available(
            venue_id="demo_paris_001",
            category="restaurant",
            date="2025-01-15",
            time="19:30",
            party_size=4
        )
        assert result is True
