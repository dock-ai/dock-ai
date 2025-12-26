"""Dock AI MCP Server - Booking platform aggregator."""

from fastmcp import FastMCP

from .adapters import DemoAdapter, get_adapter_for_provider
from .categories import (
    get_filters_for_category,
    get_available_categories,
    get_available_tools,
    validate_params,
    is_valid_category,
)
from .registry import Registry


class DockAIError(Exception):
    """Base exception for Dock AI errors."""
    pass


class ValidationError(DockAIError):
    """Invalid input parameters."""
    pass


class VenueNotFoundError(DockAIError):
    """Venue not found in registry."""
    pass


class BookingNotFoundError(DockAIError):
    """Booking not found."""
    pass


class ProviderError(DockAIError):
    """Error from booking provider."""
    pass

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

# Initialize adapters and registry
demo_adapter = DemoAdapter()
registry = Registry()


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
        return {
            "error": f"Unknown category '{category}' or tool '{tool}'",
            "available_categories": get_available_categories(),
            "available_tools": get_available_tools()
        }

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
    # Validate category
    if not is_valid_category(category):
        return {
            "error": f"Invalid category: {category}",
            "available_categories": get_available_categories()
        }

    # Basic validation
    if not city or not city.strip():
        return {"error": "city is required"}

    if not date or len(date) != 10:
        return {"error": "date must be in YYYY-MM-DD format"}

    if not isinstance(party_size, int) or party_size < 1:
        return {"error": "party_size must be a positive integer"}

    try:
        venues = await demo_adapter.search(
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
    except Exception as e:
        return {
            "error": f"Search failed: {str(e)}",
            "category": category,
            "city": city
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
        List of time slots with:
        - time: Time in HH:MM format
        - available: true/false
        - covers_available: Number of seats/slots available

    Examples:
        # Restaurant
        check_availability(
            venue_id="demo_paris_001",
            category="restaurant",
            params={"date": "2025-01-15", "party_size": 4}
        )

        # Hair salon
        check_availability(
            venue_id="demo_paris_hair_001",
            category="hair_salon",
            params={"date": "2025-01-15", "service": "Haircut"}
        )
    """
    # Validate category
    if not is_valid_category(category):
        return {
            "error": f"Invalid category: {category}",
            "available_categories": get_available_categories()
        }

    # Validate params
    is_valid, error_msg = validate_params(category, "check_availability", params)
    if not is_valid:
        return {
            "error": error_msg,
            "expected_params": get_filters_for_category(category, "check_availability")
        }

    # Get adapter
    mapping = registry.get_mapping(venue_id)
    if mapping and mapping.provider:
        try:
            adapter = get_adapter_for_provider(mapping.provider)
        except ValueError:
            adapter = demo_adapter
    else:
        adapter = demo_adapter

    try:
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
    except Exception as e:
        return {
            "error": f"Failed to check availability: {str(e)}",
            "venue_id": venue_id
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
        Booking confirmation with:
        - id: Booking reference number
        - venue_name: Venue name
        - params: Booking details
        - status: "confirmed" if successful

    Examples:
        # Restaurant booking
        book(
            venue_id="demo_paris_001",
            category="restaurant",
            params={"date": "2025-01-15", "time": "19:30", "party_size": 4},
            customer_name="John Doe",
            customer_email="john@example.com",
            customer_phone="+33612345678"
        )

        # Hair salon booking
        book(
            venue_id="demo_paris_hair_001",
            category="hair_salon",
            params={"date": "2025-01-15", "time": "14:00", "service": "Haircut"},
            customer_name="Jane Doe",
            customer_email="jane@example.com",
            customer_phone="+33612345678"
        )
    """
    # Validate category
    if not is_valid_category(category):
        return {
            "error": f"Invalid category: {category}",
            "available_categories": get_available_categories()
        }

    # Validate params
    is_valid, error_msg = validate_params(category, "book", params)
    if not is_valid:
        return {
            "error": error_msg,
            "expected_params": get_filters_for_category(category, "book")
        }

    # Validate customer info
    if not customer_name or not customer_name.strip():
        return {"error": "customer_name is required"}
    if not customer_email or "@" not in customer_email:
        return {"error": "Valid customer_email is required"}
    if not customer_phone or not customer_phone.strip():
        return {"error": "customer_phone is required"}

    # Get adapter
    mapping = registry.get_mapping(venue_id)
    if mapping and mapping.provider:
        try:
            adapter = get_adapter_for_provider(mapping.provider)
        except ValueError:
            adapter = demo_adapter
    else:
        adapter = demo_adapter

    try:
        booking = await adapter.book(
            venue_id=venue_id,
            category=category,
            params=params,
            customer_name=customer_name.strip(),
            customer_email=customer_email.strip(),
            customer_phone=customer_phone.strip()
        )
        return booking.model_dump()
    except Exception as e:
        return {
            "error": f"Failed to create booking: {str(e)}",
            "venue_id": venue_id
        }


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


@mcp.tool
async def get_venue_details(venue_id: str) -> dict:
    """
    Get detailed information about a venue.

    Args:
        venue_id: Venue identifier

    Returns:
        Venue details including:
        - venue_id: Internal identifier
        - name: Venue name
        - category: Business category
        - address: Full address
        - city: City
        - country: Country code
        - domain: Website (if available)
        - metadata: Category-specific info (cuisine, services, etc.)
        - provider: Booking provider

    Example:
        get_venue_details(venue_id="demo_paris_001")
    """
    venue = registry.get_venue(venue_id)
    if venue:
        return venue.model_dump()
    return {
        "error": f"Venue not found: {venue_id}",
        "venue_id": venue_id
    }


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
        List of venues matching the filters

    Examples:
        list_venues()  # All venues
        list_venues(category="restaurant")
        list_venues(city="Paris")
        list_venues(category="hair_salon", city="London")
    """
    if category and not is_valid_category(category):
        return {
            "error": f"Invalid category: {category}",
            "available_categories": get_available_categories()
        }

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
        Booking status including:
        - booking_id: Booking reference
        - status: confirmed, cancelled, completed, no_show
        - venue_name: Venue name
        - params: Booking details (date, time, etc.)

    Example:
        get_booking_status(booking_id="booking_abc123")
    """
    # For now, use demo adapter (real implementation would query bookings table)
    # This is a placeholder that returns mock data
    return {
        "booking_id": booking_id,
        "status": "confirmed",
        "message": "Booking status lookup not yet implemented for production. Demo mode returns confirmed."
    }


def main():
    """Main entry point."""
    mcp.run()


if __name__ == "__main__":
    main()
