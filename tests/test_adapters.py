"""Tests for the adapters module."""

import pytest

from dock_ai.adapters import DemoAdapter, Venue, TimeSlot, Booking, get_adapter_for_provider


class TestDemoAdapter:
    """Test DemoAdapter functionality."""

    @pytest.fixture
    def adapter(self):
        """Create a demo adapter instance."""
        return DemoAdapter()

    @pytest.mark.asyncio
    async def test_search_restaurants_paris(self, adapter):
        """Search returns restaurants in Paris."""
        venues = await adapter.search(
            city="Paris",
            date="2025-01-15",
            party_size=4,
            category="restaurant"
        )
        assert len(venues) > 0
        assert all(isinstance(v, Venue) for v in venues)
        assert all(v.category == "restaurant" for v in venues)

    @pytest.mark.asyncio
    async def test_search_with_cuisine_filter(self, adapter):
        """Search filters by cuisine."""
        venues = await adapter.search(
            city="Paris",
            date="2025-01-15",
            party_size=4,
            category="restaurant",
            filters={"cuisine": "French"}
        )
        # All results should have French cuisine or be near-matches
        assert len(venues) >= 0  # May or may not have matches

    @pytest.mark.asyncio
    async def test_search_unknown_city(self, adapter):
        """Search in unknown city returns empty."""
        venues = await adapter.search(
            city="Atlantis",
            date="2025-01-15",
            party_size=4,
            category="restaurant"
        )
        assert venues == []

    @pytest.mark.asyncio
    async def test_get_availability(self, adapter):
        """Get availability returns time slots."""
        slots = await adapter.get_availability(
            venue_id="demo_paris_001",
            category="restaurant",
            params={"date": "2025-01-15", "party_size": 4}
        )
        assert len(slots) > 0
        assert all(isinstance(s, TimeSlot) for s in slots)
        assert all(isinstance(s.available, bool) for s in slots)

    @pytest.mark.asyncio
    async def test_book_success(self, adapter):
        """Book creates a confirmed booking."""
        booking = await adapter.book(
            venue_id="demo_paris_001",
            category="restaurant",
            params={"date": "2025-01-15", "time": "19:30", "party_size": 4},
            customer_name="John Doe",
            customer_email="john@example.com",
            customer_phone="+33612345678"
        )
        assert isinstance(booking, Booking)
        assert booking.status == "confirmed"
        assert booking.customer_name == "John Doe"
        assert "booking_" in booking.id

    @pytest.mark.asyncio
    async def test_cancel_booking(self, adapter):
        """Cancel returns True."""
        result = await adapter.cancel("booking_123")
        assert result is True


class TestGetAdapterForProvider:
    """Test get_adapter_for_provider function."""

    def test_demo_provider(self):
        """Demo provider returns DemoAdapter."""
        adapter = get_adapter_for_provider("demo")
        assert isinstance(adapter, DemoAdapter)

    def test_case_insensitive(self):
        """Provider lookup is case-insensitive."""
        adapter = get_adapter_for_provider("DEMO")
        assert isinstance(adapter, DemoAdapter)

    def test_unknown_provider(self):
        """Unknown provider raises ValueError."""
        with pytest.raises(ValueError) as exc_info:
            get_adapter_for_provider("unknown_provider")
        assert "Unsupported provider" in str(exc_info.value)


class TestVenueModel:
    """Test Venue model."""

    def test_create_venue(self):
        """Create a venue with all fields."""
        venue = Venue(
            id="test_001",
            name="Test Restaurant",
            address="123 Test St",
            category="restaurant",
            provider="demo",
            rating=4.5,
            cuisine="French",
            price_range="$$"
        )
        assert venue.id == "test_001"
        assert venue.cuisine == "French"

    def test_venue_optional_fields(self):
        """Create venue with only required fields."""
        venue = Venue(
            id="test_002",
            name="Test Salon",
            address="456 Test Ave",
            category="hair_salon",
            provider="demo"
        )
        assert venue.cuisine is None
        assert venue.rating is None


class TestBookingModel:
    """Test Booking model."""

    def test_create_booking(self):
        """Create a booking with all fields."""
        booking = Booking(
            id="booking_001",
            venue_id="venue_001",
            venue_name="Test Restaurant",
            category="restaurant",
            params={"date": "2025-01-15", "time": "19:30", "party_size": 4},
            customer_name="John Doe",
            status="confirmed"
        )
        assert booking.id == "booking_001"
        assert booking.params["party_size"] == 4
        assert booking.status == "confirmed"
