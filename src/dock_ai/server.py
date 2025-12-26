"""Dock AI MCP Server - Booking platform aggregator."""

from fastmcp import FastMCP

from .adapters import DemoAdapter, get_adapter_for_provider
from .categories import get_filters_for_category, get_available_categories
from .registry import Registry

# Initialize FastMCP server
mcp = FastMCP(
    name="dock-ai",
    instructions="""
        Dock AI aggregates multiple booking platforms into a unified interface.

        IMPORTANT: Before calling search_venues, always call get_filters(category)
        first to discover available filter options for that business category.

        Typical flow:
        1. get_filters(category="restaurant") → see available cuisines, price ranges
        2. search_venues(category="restaurant", city="Paris", ...) → find venues
        3. check_availability(venue_id, date, party_size) → see time slots
        4. book(...) → make reservation
    """
)

# Initialize adapters and registry
demo_adapter = DemoAdapter()
registry = Registry()


@mcp.tool
async def get_filters(category: str) -> dict:
    """
    Get available search filters for a business category.

    Call this BEFORE search_venues to discover what filters are available.

    Args:
        category: Business category (restaurant, hair_salon, spa, fitness)

    Returns:
        Dictionary of filter names and their possible values.

    Example:
        get_filters(category="restaurant")
        # Returns: {"cuisine": ["French", "Japanese", ...], "price_range": ["$", "$$", ...]}
    """
    filters = get_filters_for_category(category)

    if not filters:
        return {
            "error": f"Unknown category: {category}",
            "available_categories": get_available_categories()
        }

    return {
        "category": category.lower().replace(" ", "_"),
        "filters": filters
    }


@mcp.tool
async def search_venues(
    category: str,
    city: str,
    date: str,
    party_size: int,
    filters: dict | None = None
) -> list[dict]:
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
        List of venues with:
        - id: Unique identifier
        - name: Venue name
        - address: Full address
        - category: Business category
        - subcategory: Specific type (cuisine, service, etc.)
        - rating: Rating (out of 5)
        - provider: Source platform

    Example:
        search_venues(
            category="restaurant",
            city="Paris",
            date="2025-01-15",
            party_size=4,
            filters={"cuisine": "French", "price_range": "$$"}
        )
    """
    venues = await demo_adapter.search(
        city=city,
        date=date,
        party_size=party_size,
        category=category,
        filters=filters
    )
    return [v.model_dump() for v in venues]


@mcp.tool
async def check_availability(
    venue_id: str,
    date: str,
    party_size: int
) -> list[dict]:
    """
    Check available time slots for a venue.

    Args:
        venue_id: Venue identifier (from search_venues)
        date: Date in YYYY-MM-DD format
        party_size: Number of guests

    Returns:
        List of time slots with:
        - time: Time in HH:MM format
        - available: true/false
        - covers_available: Number of seats available

    Example:
        check_availability(venue_id="demo_paris_001", date="2025-01-15", party_size=4)
    """
    mapping = registry.get_mapping(venue_id)
    if mapping:
        adapter = get_adapter_for_provider(mapping.provider)
    else:
        adapter = demo_adapter  # Default fallback

    slots = await adapter.get_availability(
        venue_id=venue_id,
        date=date,
        party_size=party_size
    )
    return [s.model_dump() for s in slots]


@mcp.tool
async def book(
    venue_id: str,
    date: str,
    time: str,
    party_size: int,
    customer_name: str,
    customer_email: str,
    customer_phone: str
) -> dict:
    """
    Book a slot at a venue.

    Args:
        venue_id: Venue identifier
        date: Date in YYYY-MM-DD format
        time: Time in HH:MM format (e.g., "19:30")
        party_size: Number of guests
        customer_name: Full name of the guest
        customer_email: Email address
        customer_phone: Phone number with country code

    Returns:
        Booking confirmation with:
        - id: Booking reference number
        - venue_name: Venue name
        - date, time, party_size: Booking details
        - status: "confirmed" if successful

    Example:
        book(
            venue_id="demo_paris_001",
            date="2025-01-15",
            time="19:30",
            party_size=4,
            customer_name="John Doe",
            customer_email="john@example.com",
            customer_phone="+33612345678"
        )
    """
    mapping = registry.get_mapping(venue_id)
    if mapping:
        adapter = get_adapter_for_provider(mapping.provider)
    else:
        adapter = demo_adapter

    booking = await adapter.book(
        venue_id=venue_id,
        date=date,
        time=time,
        party_size=party_size,
        customer_name=customer_name,
        customer_email=customer_email,
        customer_phone=customer_phone
    )
    return booking.model_dump()


@mcp.tool
async def cancel(booking_id: str) -> dict:
    """
    Cancel an existing booking.

    Args:
        booking_id: Booking reference (from book response)

    Returns:
        - success: true if cancelled successfully
        - message: Confirmation message

    Example:
        cancel(booking_id="booking_abc123")
    """
    success = await demo_adapter.cancel(booking_id)
    return {
        "success": success,
        "booking_id": booking_id,
        "message": "Booking cancelled successfully" if success else "Failed to cancel booking"
    }


@mcp.tool
async def find_venue_by_domain(domain: str) -> dict | None:
    """
    Find a venue by its website domain.

    Useful when an agent knows a venue's website but not which
    booking platform it uses.

    Args:
        domain: Venue website domain (e.g., "venue-example.com")

    Returns:
        Venue mapping or None if not found:
        - venue_id: Internal identifier
        - provider: Booking platform
        - name: Venue name
        - domain: Website domain

    Example:
        find_venue_by_domain(domain="venue-example.com")
    """
    mapping = registry.find_by_domain(domain)
    if mapping:
        return mapping.model_dump()
    return None


def main():
    """Main entry point."""
    mcp.run()


if __name__ == "__main__":
    main()
