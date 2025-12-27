"""Dock AI MCP Server - Booking platform aggregator."""

import json
import uuid
from datetime import datetime

from fastmcp import FastMCP
from fastmcp.exceptions import ToolError

from .adapters import DemoAdapter, get_adapter_for_provider
from .categories import (
    get_filters_for_category,
    get_available_categories,
    get_available_tools,
    validate_params,
    is_valid_category,
)
from .registry import Registry
from .registry.database import get_client


# Initialize FastMCP server
mcp = FastMCP(
    name="dock-ai",
    instructions="""
        Dock AI aggregates multiple booking platforms into a unified interface.

        IMPORTANT: Before each tool call, use get_filters(category, tool) to discover
        the required parameters for that category.

        Flow:
        1. get_filters(category, "search") → see available search filters
        2. search_venues(category, city, date, party_size, filters) → find venues
        3. get_filters(category, "check_availability") → see required params
        4. check_availability(venue_id, category, params) → see time slots
        5. get_filters(category, "book") → see required booking params
        6. book(venue_id, category, params, customer_info) → make reservation

        Parameters vary by category:
        - restaurant: uses party_size
        - hair_salon: uses service, duration (no party_size)
        - spa: uses service, duration
        - fitness: uses activity
    """
)

# Initialize registry
registry = Registry()


def get_adapter_for_venue(venue_id: str) -> tuple:
    """Get the appropriate adapter for a venue.

    Returns:
        Tuple of (adapter, provider_name)
    """
    mapping = registry.get_mapping(venue_id)
    if mapping and mapping.provider:
        try:
            adapter = get_adapter_for_provider(mapping.provider)
            return adapter, mapping.provider
        except ValueError:
            pass
    # Fallback to demo
    return DemoAdapter(), "demo"


class BookingManager:
    """Manages booking persistence and optimistic locking."""

    @staticmethod
    def generate_booking_id() -> str:
        """Generate a unique booking ID."""
        return f"booking_{uuid.uuid4().hex[:12]}"

    @staticmethod
    async def check_slot_available(
        venue_id: str,
        category: str,
        date: str,
        time: str,
        party_size: int | None = None
    ) -> bool:
        """Check if a slot is still available (optimistic lock check).

        In production, this would check against the provider's real-time availability
        and/or our local booking records to prevent double-booking.
        """
        # Check if we already have a booking for this slot
        try:
            response = (
                get_client()
                .table("bookings")
                .select("booking_id")
                .eq("venue_id", venue_id)
                .eq("status", "confirmed")
                .execute()
            )

            # Check params for matching date/time
            for booking in response.data:
                # In production, parse params and check for conflicts
                pass

            return True  # Slot available
        except Exception:
            # If we can't check, assume available (provider will validate)
            return True

    @staticmethod
    async def persist_booking(
        booking_id: str,
        venue_id: str,
        provider: str,
        provider_booking_id: str | None,
        category: str,
        params: dict,
        customer_name: str,
        customer_email: str,
        customer_phone: str | None,
        status: str = "confirmed"
    ) -> dict:
        """Persist a booking to the database."""
        try:
            booking_data = {
                "booking_id": booking_id,
                "venue_id": venue_id,
                "provider": provider,
                "provider_booking_id": provider_booking_id,
                "category": category,
                "params": json.dumps(params),
                "customer_name": customer_name,
                "customer_email": customer_email,
                "customer_phone": customer_phone,
                "status": status,
            }

            response = (
                get_client()
                .table("bookings")
                .insert(booking_data)
                .execute()
            )

            if response.data:
                return response.data[0]
            return booking_data
        except Exception as e:
            # Log but don't fail - booking was created with provider
            print(f"Warning: Failed to persist booking {booking_id}: {e}")
            return {"booking_id": booking_id, "persisted": False}

    @staticmethod
    async def get_booking(booking_id: str) -> dict | None:
        """Get a booking from the database."""
        try:
            response = (
                get_client()
                .table("bookings")
                .select("*")
                .eq("booking_id", booking_id)
                .execute()
            )

            if response.data:
                booking = response.data[0]
                # Parse params back to dict
                if isinstance(booking.get("params"), str):
                    booking["params"] = json.loads(booking["params"])
                return booking
            return None
        except Exception:
            return None

    @staticmethod
    async def update_booking_status(booking_id: str, status: str) -> bool:
        """Update booking status in the database."""
        try:
            response = (
                get_client()
                .table("bookings")
                .update({"status": status, "updated_at": datetime.utcnow().isoformat()})
                .eq("booking_id", booking_id)
                .execute()
            )
            return bool(response.data)
        except Exception:
            return False

    @staticmethod
    async def list_bookings(
        customer_email: str | None = None,
        venue_id: str | None = None,
        status: str | None = None
    ) -> list[dict]:
        """List bookings with optional filters."""
        try:
            query = get_client().table("bookings").select("*")

            if customer_email:
                query = query.eq("customer_email", customer_email)
            if venue_id:
                query = query.eq("venue_id", venue_id)
            if status:
                query = query.eq("status", status)

            response = query.order("created_at", desc=True).execute()

            bookings = []
            for booking in response.data:
                if isinstance(booking.get("params"), str):
                    booking["params"] = json.loads(booking["params"])
                bookings.append(booking)

            return bookings
        except Exception:
            return []


# Booking manager instance
booking_manager = BookingManager()


@mcp.tool
async def get_filters(category: str, tool: str = "search") -> dict:
    """
    Get available parameters for a category and tool.

    Call this BEFORE using search_venues, check_availability, or book
    to discover what parameters are required for that category.

    Args:
        category: Business category (restaurant, hair_salon, spa, fitness)
        tool: Tool name (search, check_availability, book)

    Returns:
        Dictionary of parameter names and their possible values or schema.

    Examples:
        get_filters(category="restaurant", tool="search")
        # Returns: {"cuisine": ["French", ...], "price_range": ["$", ...]}

        get_filters(category="restaurant", tool="book")
        # Returns: {"party_size": {"type": "integer", "min": 1, "max": 20}, ...}

        get_filters(category="hair_salon", tool="book")
        # Returns: {"service": {...}, "duration": {...}}  # No party_size!
    """
    filters = get_filters_for_category(category, tool)

    if not filters:
        raise ToolError(
            f"Unknown category '{category}' or tool '{tool}'. "
            f"Available categories: {', '.join(get_available_categories())}. "
            f"Available tools: {', '.join(get_available_tools())}."
        )

    return {
        "category": category.lower().replace(" ", "_"),
        "tool": tool.lower(),
        "parameters": filters
    }


@mcp.tool
async def search_venues(
    category: str,
    city: str,
    date: str,
    party_size: int,
    filters: dict | None = None
) -> dict:
    """
    Search for available venues in a city.

    IMPORTANT: Call get_filters(category) first to see available filter options.

    Args:
        category: Business type (restaurant, hair_salon, spa, fitness)
        city: City to search (e.g., "Paris", "London", "New York")
        date: Desired date in YYYY-MM-DD format (e.g., "2025-01-15")
        party_size: Number of guests (e.g., 2, 4, 6)
        filters: Optional filters from get_filters (e.g., {"cuisine": "French", "price_range": "$$"})

    Returns:
        List of venues with id, name, address, category, rating, provider
    """
    # Validate category
    if not is_valid_category(category):
        raise ToolError(
            f"Invalid category: {category}. "
            f"Available: {', '.join(get_available_categories())}"
        )

    # Basic validation
    if not city or not city.strip():
        raise ToolError("city is required")

    if not date or len(date) != 10:
        raise ToolError("date must be in YYYY-MM-DD format")

    if not isinstance(party_size, int) or party_size < 1:
        raise ToolError("party_size must be a positive integer")

    # Get all adapters that serve this city/category
    # For now, use demo adapter. In production, query registry for providers
    adapter, _ = get_adapter_for_venue(f"search_{city}_{category}")

    venues = await adapter.search(
        city=city.strip(),
        date=date,
        party_size=party_size,
        category=category.lower(),
        filters=filters
    )

    return {
        "count": len(venues),
        "search": {
            "category": category,
            "city": city,
            "date": date,
            "party_size": party_size,
            "filters": filters
        },
        "venues": [v.model_dump() for v in venues]
    }


@mcp.tool
async def check_availability(
    venue_id: str,
    category: str,
    params: dict
) -> dict:
    """
    Check available time slots for a venue.

    IMPORTANT: Call get_filters(category, "check_availability") first
    to see required parameters for this category.

    Args:
        venue_id: Venue identifier (from search_venues)
        category: Business category (restaurant, hair_salon, spa, fitness)
        params: Category-specific parameters from get_filters:
            - restaurant: {"date": "2025-01-15", "party_size": 4}
            - hair_salon: {"date": "2025-01-15", "service": "Haircut"}
            - spa: {"date": "2025-01-15", "service": "Massage", "duration": "60min"}

    Returns:
        List of time slots with time, available, covers_available
    """
    # Validate category
    if not is_valid_category(category):
        raise ToolError(
            f"Invalid category: {category}. "
            f"Available: {', '.join(get_available_categories())}"
        )

    # Validate params
    is_valid, error_msg = validate_params(category, "check_availability", params)
    if not is_valid:
        expected = get_filters_for_category(category, "check_availability")
        raise ToolError(f"{error_msg}. Expected params: {expected}")

    # Get adapter for this venue
    adapter, _ = get_adapter_for_venue(venue_id)

    slots = await adapter.get_availability(
        venue_id=venue_id,
        category=category,
        params=params
    )

    return {
        "venue_id": venue_id,
        "category": category,
        "params": params,
        "slots": [s.model_dump() for s in slots]
    }


@mcp.tool
async def book(
    venue_id: str,
    category: str,
    params: dict,
    customer_name: str,
    customer_email: str,
    customer_phone: str
) -> dict:
    """
    Book a slot at a venue.

    IMPORTANT: Call get_filters(category, "book") first
    to see required parameters for this category.

    Args:
        venue_id: Venue identifier
        category: Business category (restaurant, hair_salon, spa, fitness)
        params: Category-specific parameters from get_filters:
            - restaurant: {"date": "2025-01-15", "time": "19:30", "party_size": 4}
            - hair_salon: {"date": "2025-01-15", "time": "14:00", "service": "Haircut"}
            - spa: {"date": "2025-01-15", "time": "10:00", "service": "Massage", "duration": "60min"}
        customer_name: Full name of the guest
        customer_email: Email address
        customer_phone: Phone number with country code

    Returns:
        Booking confirmation with id, venue_name, params, status
    """
    # Validate category
    if not is_valid_category(category):
        raise ToolError(
            f"Invalid category: {category}. "
            f"Available: {', '.join(get_available_categories())}"
        )

    # Validate params
    is_valid, error_msg = validate_params(category, "book", params)
    if not is_valid:
        expected = get_filters_for_category(category, "book")
        raise ToolError(f"{error_msg}. Expected params: {expected}")

    # Validate customer info
    if not customer_name or not customer_name.strip():
        raise ToolError("customer_name is required")
    if not customer_email or "@" not in customer_email:
        raise ToolError("Valid customer_email is required")
    if not customer_phone or not customer_phone.strip():
        raise ToolError("customer_phone is required")

    # Check slot availability (optimistic lock)
    date = params.get("date")
    time = params.get("time")
    party_size = params.get("party_size")

    if not await booking_manager.check_slot_available(
        venue_id, category, date, time, party_size
    ):
        raise ToolError(
            f"Slot no longer available at {time} on {date}. "
            "Please check availability again."
        )

    # Get adapter for this venue
    adapter, provider = get_adapter_for_venue(venue_id)

    # Create booking with provider
    booking = await adapter.book(
        venue_id=venue_id,
        category=category,
        params=params,
        customer_name=customer_name.strip(),
        customer_email=customer_email.strip(),
        customer_phone=customer_phone.strip()
    )

    # Persist to our database
    await booking_manager.persist_booking(
        booking_id=booking.id,
        venue_id=venue_id,
        provider=provider,
        provider_booking_id=booking.id,  # Same as our ID for demo
        category=category,
        params=params,
        customer_name=customer_name.strip(),
        customer_email=customer_email.strip(),
        customer_phone=customer_phone.strip(),
        status=booking.status
    )

    return booking.model_dump()


@mcp.tool
async def cancel(booking_id: str) -> dict:
    """
    Cancel an existing booking.

    Args:
        booking_id: Booking reference (from book response)

    Returns:
        Cancellation confirmation with success status and message
    """
    # Get booking from database
    booking = await booking_manager.get_booking(booking_id)

    if not booking:
        raise ToolError(f"Booking not found: {booking_id}")

    if booking.get("status") == "cancelled":
        raise ToolError(f"Booking {booking_id} is already cancelled")

    # Get adapter and cancel with provider
    adapter, _ = get_adapter_for_venue(booking.get("venue_id", ""))
    success = await adapter.cancel(booking_id)

    if success:
        # Update our database
        await booking_manager.update_booking_status(booking_id, "cancelled")
        return {
            "success": True,
            "booking_id": booking_id,
            "message": "Booking cancelled successfully"
        }
    else:
        raise ToolError(f"Failed to cancel booking {booking_id} with provider")


@mcp.tool
async def find_venue_by_domain(domain: str) -> dict:
    """
    Find a venue by its website domain.

    Useful when an agent knows a venue's website but not which
    booking platform it uses.

    Args:
        domain: Venue website domain (e.g., "venue-example.com")

    Returns:
        Venue mapping with venue_id, provider, name, domain
    """
    mapping = registry.find_by_domain(domain)
    if mapping:
        return mapping.model_dump()
    raise ToolError(f"No venue found for domain: {domain}")


@mcp.tool
async def get_venue_details(venue_id: str) -> dict:
    """
    Get detailed information about a venue.

    Args:
        venue_id: Venue identifier

    Returns:
        Venue details including venue_id, name, category, address, city,
        country, domain, metadata, provider
    """
    venue = registry.get_venue(venue_id)
    if venue:
        return venue.model_dump()
    raise ToolError(f"Venue not found: {venue_id}")


@mcp.tool
async def list_venues(
    category: str | None = None,
    city: str | None = None
) -> dict:
    """
    List all venues with optional filters.

    Args:
        category: Filter by category (restaurant, hair_salon, spa, fitness)
        city: Filter by city (case-insensitive)

    Returns:
        List of venues matching the filters with count
    """
    if category and not is_valid_category(category):
        raise ToolError(
            f"Invalid category: {category}. "
            f"Available: {', '.join(get_available_categories())}"
        )

    venues = registry.list_venues(category=category, city=city)
    return {
        "count": len(venues),
        "filters": {"category": category, "city": city},
        "venues": [v.model_dump() for v in venues]
    }


@mcp.tool
async def get_booking_status(booking_id: str) -> dict:
    """
    Get the status of an existing booking.

    Args:
        booking_id: Booking reference (from book response)

    Returns:
        Booking status including booking_id, status, venue_id,
        category, params, customer info
    """
    booking = await booking_manager.get_booking(booking_id)

    if not booking:
        raise ToolError(f"Booking not found: {booking_id}")

    return {
        "booking_id": booking.get("booking_id"),
        "status": booking.get("status"),
        "venue_id": booking.get("venue_id"),
        "category": booking.get("category"),
        "params": booking.get("params"),
        "customer_name": booking.get("customer_name"),
        "customer_email": booking.get("customer_email"),
        "created_at": booking.get("created_at"),
    }


@mcp.tool
async def list_bookings(
    customer_email: str | None = None,
    venue_id: str | None = None,
    status: str | None = None
) -> dict:
    """
    List bookings with optional filters.

    Args:
        customer_email: Filter by customer email
        venue_id: Filter by venue
        status: Filter by status (confirmed, cancelled, completed, no_show)

    Returns:
        List of bookings matching the filters
    """
    bookings = await booking_manager.list_bookings(
        customer_email=customer_email,
        venue_id=venue_id,
        status=status
    )

    return {
        "count": len(bookings),
        "filters": {
            "customer_email": customer_email,
            "venue_id": venue_id,
            "status": status
        },
        "bookings": bookings
    }


def main():
    """Main entry point."""
    mcp.run()


if __name__ == "__main__":
    main()
