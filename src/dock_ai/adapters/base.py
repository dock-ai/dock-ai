"""Base adapter class and shared models for booking providers."""

from abc import ABC, abstractmethod
from pydantic import BaseModel


class Venue(BaseModel):
    """Venue information from a booking provider."""
    id: str
    name: str
    address: str
    category: str  # "restaurant", "hair_salon", "spa", etc.
    provider: str
    rating: float | None = None
    # Category-specific attributes (matches filter names)
    cuisine: str | None = None      # for restaurants
    service: str | None = None      # for hair_salon, spa
    activity: str | None = None     # for fitness
    price_range: str | None = None  # for any category


class TimeSlot(BaseModel):
    """Available time slot for a venue."""
    time: str  # "19:00"
    available: bool
    covers_available: int


class Booking(BaseModel):
    """Confirmed booking information."""
    id: str
    venue_id: str
    venue_name: str
    date: str
    time: str
    party_size: int
    customer_name: str
    status: str  # "confirmed", "cancelled"


class BaseAdapter(ABC):
    """Abstract base class for all booking provider adapters."""

    provider_name: str

    @abstractmethod
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

        Args:
            city: City name to search in
            date: Date in YYYY-MM-DD format
            party_size: Number of people
            category: Business category (restaurant, hair_salon, spa, etc.)
            filters: Optional filters (e.g., {"cuisine": "French"})

        Returns:
            List of available venues
        """
        ...

    @abstractmethod
    async def get_availability(
        self,
        venue_id: str,
        date: str,
        party_size: int
    ) -> list[TimeSlot]:
        """
        Get available time slots for a venue.

        Args:
            venue_id: Venue identifier
            date: Date in YYYY-MM-DD format
            party_size: Number of people

        Returns:
            List of time slots with availability
        """
        ...

    @abstractmethod
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

        Args:
            venue_id: Venue identifier
            date: Date in YYYY-MM-DD format
            time: Time in HH:MM format
            party_size: Number of people
            customer_name: Customer's full name
            customer_email: Customer's email address
            customer_phone: Customer's phone number

        Returns:
            Confirmed booking details
        """
        ...

    @abstractmethod
    async def cancel(self, booking_id: str) -> bool:
        """
        Cancel a booking.

        Args:
            booking_id: Booking identifier

        Returns:
            True if cancellation was successful
        """
        ...
