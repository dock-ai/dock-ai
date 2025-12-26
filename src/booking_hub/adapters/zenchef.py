"""Zenchef booking provider adapter with mock data."""

import uuid
from datetime import datetime
import httpx

from .base import BaseAdapter, Restaurant, TimeSlot, Booking


# Mock restaurant database by city
MOCK_RESTAURANTS = {
    "paris": [
        {
            "id": "zenchef_paris_001",
            "name": "Le Comptoir du Relais",
            "address": "9 Carrefour de l'Odéon, 75006 Paris",
            "cuisine": "French",
            "rating": 4.5,
        },
        {
            "id": "zenchef_paris_002",
            "name": "Septime",
            "address": "80 Rue de Charonne, 75011 Paris",
            "cuisine": "Contemporary",
            "rating": 4.8,
        },
        {
            "id": "zenchef_paris_003",
            "name": "L'Ami Jean",
            "address": "27 Rue Malar, 75007 Paris",
            "cuisine": "Basque",
            "rating": 4.6,
        },
        {
            "id": "zenchef_paris_004",
            "name": "Frenchie",
            "address": "5 Rue du Nil, 75002 Paris",
            "cuisine": "French",
            "rating": 4.7,
        },
    ],
    "lyon": [
        {
            "id": "zenchef_lyon_001",
            "name": "Paul Bocuse",
            "address": "40 Quai de la Plage, 69660 Collonges-au-Mont-d'Or",
            "cuisine": "French",
            "rating": 4.9,
        },
        {
            "id": "zenchef_lyon_002",
            "name": "Le Neuvième Art",
            "address": "173 Rue Cuvier, 69006 Lyon",
            "cuisine": "Contemporary",
            "rating": 4.7,
        },
        {
            "id": "zenchef_lyon_003",
            "name": "Takao Takano",
            "address": "33 Rue Malesherbes, 69006 Lyon",
            "cuisine": "Japanese",
            "rating": 4.8,
        },
    ],
    "marseille": [
        {
            "id": "zenchef_marseille_001",
            "name": "Le Petit Nice",
            "address": "Anse de Maldormé, 13007 Marseille",
            "cuisine": "Mediterranean",
            "rating": 4.8,
        },
        {
            "id": "zenchef_marseille_002",
            "name": "L'Épuisette",
            "address": "158 Rue du Vallon des Auffes, 13007 Marseille",
            "cuisine": "Seafood",
            "rating": 4.6,
        },
        {
            "id": "zenchef_marseille_003",
            "name": "Une Table au Sud",
            "address": "2 Quai du Port, 13002 Marseille",
            "cuisine": "French",
            "rating": 4.5,
        },
        {
            "id": "zenchef_marseille_004",
            "name": "Alcyone",
            "address": "Hôtel Intercontinental, 13007 Marseille",
            "cuisine": "Contemporary",
            "rating": 4.7,
        },
    ],
    "london": [
        {
            "id": "zenchef_london_001",
            "name": "The Ledbury",
            "address": "127 Ledbury Road, London W11 2AQ",
            "cuisine": "British",
            "rating": 4.8,
        },
        {
            "id": "zenchef_london_002",
            "name": "Dishoom",
            "address": "7 Boundary St, London E2 7JE",
            "cuisine": "Indian",
            "rating": 4.6,
        },
        {
            "id": "zenchef_london_003",
            "name": "St. John",
            "address": "26 St John St, London EC1M 4AY",
            "cuisine": "British",
            "rating": 4.7,
        },
    ],
}


class ZenchefAdapter(BaseAdapter):
    """Zenchef booking provider adapter (currently using mock data)."""

    provider_name = "zenchef"

    def __init__(self, api_key: str | None = None):
        """
        Initialize Zenchef adapter.

        Args:
            api_key: Optional API key for Zenchef API (not used in mock mode)
        """
        self.api_key = api_key
        self.base_url = "https://api.zenchef.com/v1"  # Mock URL
        self.client = httpx.AsyncClient(
            headers={"Authorization": f"Bearer {api_key}"} if api_key else {}
        )

    async def search(
        self,
        city: str,
        date: str,
        party_size: int,
        cuisine: str | None = None
    ) -> list[Restaurant]:
        """
        Search for restaurants in a city.

        In production, this would call:
        GET /restaurants?city={city}&date={date}&party_size={party_size}&cuisine={cuisine}
        """
        # TODO: Replace with actual API call
        # response = await self.client.get(
        #     f"{self.base_url}/restaurants",
        #     params={
        #         "city": city,
        #         "date": date,
        #         "party_size": party_size,
        #         "cuisine": cuisine,
        #     }
        # )
        # response.raise_for_status()
        # data = response.json()

        # Mock implementation
        city_lower = city.lower()
        restaurants = MOCK_RESTAURANTS.get(city_lower, [])

        # Filter by cuisine if specified
        if cuisine:
            cuisine_lower = cuisine.lower()
            restaurants = [
                r for r in restaurants
                if cuisine_lower in r["cuisine"].lower()
            ]

        # Convert to Restaurant objects
        return [
            Restaurant(
                id=r["id"],
                name=r["name"],
                address=r["address"],
                cuisine=r["cuisine"],
                provider=self.provider_name,
                rating=r.get("rating"),
            )
            for r in restaurants
        ]

    async def get_availability(
        self,
        restaurant_id: str,
        date: str,
        party_size: int
    ) -> list[TimeSlot]:
        """
        Get available time slots for a restaurant.

        In production, this would call:
        GET /restaurants/{restaurant_id}/availability?date={date}&party_size={party_size}
        """
        # TODO: Replace with actual API call
        # response = await self.client.get(
        #     f"{self.base_url}/restaurants/{restaurant_id}/availability",
        #     params={"date": date, "party_size": party_size}
        # )
        # response.raise_for_status()
        # data = response.json()

        # Mock implementation - generate realistic time slots
        time_slots = []

        # Lunch slots: 12:00 - 14:30
        for hour in range(12, 15):
            for minute in [0, 30]:
                if hour == 14 and minute == 30:
                    continue
                time_str = f"{hour:02d}:{minute:02d}"
                # Randomly make some slots unavailable or limited
                available = hash(f"{restaurant_id}{date}{time_str}") % 3 != 0
                covers = hash(f"{restaurant_id}{date}{time_str}covers") % 20 + 5

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
                # Randomly make some slots unavailable or limited
                available = hash(f"{restaurant_id}{date}{time_str}") % 4 != 0
                covers = hash(f"{restaurant_id}{date}{time_str}covers") % 25 + 10

                time_slots.append(TimeSlot(
                    time=time_str,
                    available=available,
                    covers_available=covers if available else 0,
                ))

        return time_slots

    async def book(
        self,
        restaurant_id: str,
        date: str,
        time: str,
        party_size: int,
        customer_name: str,
        customer_email: str,
        customer_phone: str
    ) -> Booking:
        """
        Create a restaurant booking.

        In production, this would call:
        POST /bookings
        {
            "restaurant_id": "...",
            "date": "...",
            "time": "...",
            "party_size": 4,
            "customer": {
                "name": "...",
                "email": "...",
                "phone": "..."
            }
        }
        """
        # TODO: Replace with actual API call
        # response = await self.client.post(
        #     f"{self.base_url}/bookings",
        #     json={
        #         "restaurant_id": restaurant_id,
        #         "date": date,
        #         "time": time,
        #         "party_size": party_size,
        #         "customer": {
        #             "name": customer_name,
        #             "email": customer_email,
        #             "phone": customer_phone,
        #         }
        #     }
        # )
        # response.raise_for_status()
        # data = response.json()

        # Mock implementation - find restaurant name
        restaurant_name = "Unknown Restaurant"
        for city_restaurants in MOCK_RESTAURANTS.values():
            for r in city_restaurants:
                if r["id"] == restaurant_id:
                    restaurant_name = r["name"]
                    break

        # Generate a booking ID
        booking_id = f"zenchef_booking_{uuid.uuid4().hex[:12]}"

        return Booking(
            id=booking_id,
            restaurant_id=restaurant_id,
            restaurant_name=restaurant_name,
            date=date,
            time=time,
            party_size=party_size,
            customer_name=customer_name,
            status="confirmed",
        )

    async def cancel(self, booking_id: str) -> bool:
        """
        Cancel a booking.

        In production, this would call:
        DELETE /bookings/{booking_id}
        """
        # TODO: Replace with actual API call
        # response = await self.client.delete(
        #     f"{self.base_url}/bookings/{booking_id}"
        # )
        # return response.status_code == 200

        # Mock implementation - always succeed
        return True

    async def __aenter__(self):
        """Async context manager entry."""
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Async context manager exit - cleanup HTTP client."""
        await self.client.aclose()
