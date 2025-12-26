"""Base adapter class and shared models for restaurant booking providers."""

from abc import ABC, abstractmethod
from pydantic import BaseModel


class Restaurant(BaseModel):
    """Restaurant information from a booking provider."""
    id: str
    name: str
    address: str
    cuisine: str
    provider: str  # "zenchef", "planity", etc.
    rating: float | None = None


class TimeSlot(BaseModel):
    """Available time slot for a restaurant."""
    time: str  # "19:00"
    available: bool
    covers_available: int


class Booking(BaseModel):
    """Confirmed booking information."""
    id: str
    restaurant_id: str
    restaurant_name: str
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
        cuisine: str | None = None
    ) -> list[Restaurant]:
        """
        Search for restaurants in a city.

        Args:
            city: City name to search in
            date: Date in YYYY-MM-DD format
            party_size: Number of people
            cuisine: Optional cuisine filter (e.g., "Italian", "French")

        Returns:
            List of available restaurants
        """
        ...

    @abstractmethod
    async def get_availability(
        self,
        restaurant_id: str,
        date: str,
        party_size: int
    ) -> list[TimeSlot]:
        """
        Get available time slots for a restaurant.

        Args:
            restaurant_id: Restaurant identifier
            date: Date in YYYY-MM-DD format
            party_size: Number of people

        Returns:
            List of time slots with availability
        """
        ...

    @abstractmethod
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

        Args:
            restaurant_id: Restaurant identifier
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
