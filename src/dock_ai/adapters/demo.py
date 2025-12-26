"""Demo booking provider adapter with mock data.

This adapter demonstrates how to implement the BaseAdapter interface.
Use this as a template when building real provider integrations.
"""

import uuid
import httpx

from .base import BaseAdapter, Venue, TimeSlot, Booking


# Mock venue database by category and city
MOCK_VENUES = {
    "restaurant": {
        "paris": [
            {"id": "demo_paris_001", "name": "The Golden Fork", "address": "15 Avenue des Champs, 75008 Paris", "subcategory": "French", "rating": 4.5},
            {"id": "demo_paris_002", "name": "Urban Garden", "address": "42 Rue de Rivoli, 75001 Paris", "subcategory": "Contemporary", "rating": 4.8},
            {"id": "demo_paris_003", "name": "Sakura Blossom", "address": "8 Rue Saint-Anne, 75001 Paris", "subcategory": "Japanese", "rating": 4.6},
            {"id": "demo_paris_004", "name": "The Blue Oyster", "address": "23 Boulevard Saint-Germain, 75005 Paris", "subcategory": "Seafood", "rating": 4.7},
        ],
        "london": [
            {"id": "demo_london_001", "name": "The Gilded Plate", "address": "127 Kensington High Street, London W8", "subcategory": "British", "rating": 4.8},
            {"id": "demo_london_002", "name": "Spice Route", "address": "45 Brick Lane, London E1", "subcategory": "Indian", "rating": 4.6},
            {"id": "demo_london_003", "name": "The Green Table", "address": "88 Borough Market, London SE1", "subcategory": "Vegetarian", "rating": 4.7},
        ],
        "new york": [
            {"id": "demo_nyc_001", "name": "Manhattan Nights", "address": "350 5th Avenue, New York, NY 10118", "subcategory": "American", "rating": 4.7},
            {"id": "demo_nyc_002", "name": "Little Italy Kitchen", "address": "156 Mulberry Street, New York, NY 10013", "subcategory": "Italian", "rating": 4.5},
            {"id": "demo_nyc_003", "name": "Harlem Soul", "address": "2340 Frederick Douglass Blvd, New York, NY 10027", "subcategory": "Soul Food", "rating": 4.8},
        ],
    },
    "hair_salon": {
        "paris": [
            {"id": "demo_paris_hair_001", "name": "Salon Chic", "address": "10 Rue du Faubourg, 75008 Paris", "subcategory": "Unisex", "rating": 4.6},
            {"id": "demo_paris_hair_002", "name": "Cut & Color Studio", "address": "55 Avenue Montaigne, 75008 Paris", "subcategory": "Women", "rating": 4.9},
        ],
        "london": [
            {"id": "demo_london_hair_001", "name": "Blade & Fade", "address": "22 Soho Square, London W1", "subcategory": "Men", "rating": 4.7},
        ],
    },
    "spa": {
        "paris": [
            {"id": "demo_paris_spa_001", "name": "Zen Retreat", "address": "18 Place Vendome, 75001 Paris", "subcategory": "Massage", "rating": 4.8},
        ],
    },
}


class DemoAdapter(BaseAdapter):
    """Demo booking provider adapter with mock data.

    This adapter returns fake data for testing and development.
    Use it as a template when implementing real provider integrations.
    """

    provider_name = "demo"

    def __init__(self, api_key: str | None = None):
        """
        Initialize the demo adapter.

        Args:
            api_key: Optional API key (not used in demo mode)
        """
        self.api_key = api_key
        self.base_url = "https://api.example.com/v1"
        self.client = httpx.AsyncClient(
            headers={"Authorization": f"Bearer {api_key}"} if api_key else {}
        )

    async def search(
        self,
        city: str,
        date: str,
        party_size: int,
        category: str,
        filters: dict | None = None
    ) -> list[Venue]:
        """
        Search for venues in a city.

        In a real implementation, this would call:
        GET /venues?city={city}&date={date}&guests={party_size}&category={category}
        """
        category_lower = category.lower().replace(" ", "_")
        city_lower = city.lower()

        # Get venues for this category and city
        category_venues = MOCK_VENUES.get(category_lower, {})
        venues = category_venues.get(city_lower, [])

        # Apply filters
        if filters:
            # Filter by subcategory (cuisine, service, activity, etc.)
            subcategory_filter = (
                filters.get("cuisine") or
                filters.get("service") or
                filters.get("activity")
            )
            if subcategory_filter:
                filter_lower = subcategory_filter.lower()
                venues = [
                    v for v in venues
                    if filter_lower in v.get("subcategory", "").lower()
                ]

        return [
            Venue(
                id=v["id"],
                name=v["name"],
                address=v["address"],
                category=category_lower,
                subcategory=v.get("subcategory"),
                provider=self.provider_name,
                rating=v.get("rating"),
            )
            for v in venues
        ]

    async def get_availability(
        self,
        venue_id: str,
        date: str,
        party_size: int
    ) -> list[TimeSlot]:
        """
        Get available time slots for a venue.

        In a real implementation, this would call:
        GET /venues/{venue_id}/availability
        """
        time_slots = []

        # Lunch slots: 12:00 - 14:30
        for hour in range(12, 15):
            for minute in [0, 30]:
                if hour == 14 and minute == 30:
                    continue
                time_str = f"{hour:02d}:{minute:02d}"
                available = hash(f"{venue_id}{date}{time_str}") % 3 != 0
                covers = hash(f"{venue_id}{date}{time_str}covers") % 20 + 5

                time_slots.append(TimeSlot(
                    time=time_str,
                    available=available,
                    covers_available=covers if available else 0,
                ))

        # Dinner slots: 19:00 - 22:00
        for hour in range(19, 23):
            for minute in [0, 30]:
                if hour == 22 and minute == 30:
                    continue
                time_str = f"{hour:02d}:{minute:02d}"
                available = hash(f"{venue_id}{date}{time_str}") % 4 != 0
                covers = hash(f"{venue_id}{date}{time_str}covers") % 25 + 10

                time_slots.append(TimeSlot(
                    time=time_str,
                    available=available,
                    covers_available=covers if available else 0,
                ))

        return time_slots

    async def book(
        self,
        venue_id: str,
        date: str,
        time: str,
        party_size: int,
        customer_name: str,
        customer_email: str,
        customer_phone: str
    ) -> Booking:
        """
        Create a booking.

        In a real implementation, this would call:
        POST /bookings
        """
        # Find venue name
        venue_name = "Unknown Venue"
        for category_data in MOCK_VENUES.values():
            for city_venues in category_data.values():
                for v in city_venues:
                    if v["id"] == venue_id:
                        venue_name = v["name"]
                        break

        booking_id = f"booking_{uuid.uuid4().hex[:12]}"

        return Booking(
            id=booking_id,
            venue_id=venue_id,
            venue_name=venue_name,
            date=date,
            time=time,
            party_size=party_size,
            customer_name=customer_name,
            status="confirmed",
        )

    async def cancel(self, booking_id: str) -> bool:
        """
        Cancel a booking.

        In a real implementation, this would call:
        DELETE /bookings/{booking_id}
        """
        return True

    async def __aenter__(self):
        """Async context manager entry."""
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Async context manager exit."""
        await self.client.aclose()
