"""Venue registry for mapping venues to their booking providers."""

from pydantic import BaseModel

from .database import get_client


class VenueMapping(BaseModel):
    """Maps a venue to its booking provider."""
    venue_id: str
    name: str
    category: str
    address: str | None = None
    city: str | None = None
    country: str | None = None
    domain: str | None = None
    metadata: dict | None = None
    provider: str | None = None
    external_id: str | None = None


class Registry:
    """
    Maps venue IDs to their booking providers.
    Uses Supabase for persistent storage.
    """

    def _row_to_mapping(self, venue: dict, provider_info: dict | None = None) -> VenueMapping:
        """Convert database rows to VenueMapping."""
        return VenueMapping(
            venue_id=venue["venue_id"],
            name=venue["name"],
            category=venue["category"],
            address=venue.get("address"),
            city=venue.get("city"),
            country=venue.get("country"),
            domain=venue.get("domain"),
            metadata=venue.get("metadata"),
            provider=provider_info.get("provider") if provider_info else None,
            external_id=provider_info.get("external_id") if provider_info else None,
        )

    def get_venue(self, venue_id: str) -> VenueMapping | None:
        """Get venue info with its primary provider."""
        # Get venue
        venue_response = (
            get_client()
            .table("venues")
            .select("*")
            .eq("venue_id", venue_id)
            .execute()
        )
        if not venue_response.data:
            return None

        venue = venue_response.data[0]

        # Get primary provider
        provider_response = (
            get_client()
            .table("venue_providers")
            .select("provider, external_id")
            .eq("venue_id", venue_id)
            .limit(1)
            .execute()
        )
        provider_info = provider_response.data[0] if provider_response.data else None

        return self._row_to_mapping(venue, provider_info)

    def get_provider(self, venue_id: str) -> str | None:
        """Get the primary provider for a venue."""
        response = (
            get_client()
            .table("venue_providers")
            .select("provider")
            .eq("venue_id", venue_id)
            .limit(1)
            .execute()
        )
        if response.data:
            return response.data[0]["provider"]
        return None

    def get_mapping(self, venue_id: str) -> VenueMapping | None:
        """Alias for get_venue for backward compatibility."""
        return self.get_venue(venue_id)

    def find_by_domain(self, domain: str) -> VenueMapping | None:
        """Find a venue by its website domain."""
        # Normalize domain
        normalized = domain.lower().strip()
        normalized = normalized.replace("http://", "").replace("https://", "")
        normalized = normalized.replace("www.", "").rstrip("/")

        # Query with ILIKE for case-insensitive matching
        response = (
            get_client()
            .table("venues")
            .select("*")
            .ilike("domain", f"%{normalized}%")
            .execute()
        )

        # Double-check with exact normalized comparison
        for venue in response.data:
            if venue.get("domain"):
                db_domain = venue["domain"].lower().replace("www.", "").rstrip("/")
                if normalized == db_domain:
                    # Get provider info
                    provider_response = (
                        get_client()
                        .table("venue_providers")
                        .select("provider, external_id")
                        .eq("venue_id", venue["venue_id"])
                        .limit(1)
                        .execute()
                    )
                    provider_info = provider_response.data[0] if provider_response.data else None
                    return self._row_to_mapping(venue, provider_info)

        return None

    def list_venues(self, category: str | None = None, city: str | None = None) -> list[VenueMapping]:
        """List venues with optional filters."""
        query = get_client().table("venues").select("*")

        if category:
            query = query.eq("category", category)
        if city:
            query = query.ilike("city", city)

        response = query.execute()
        return [self._row_to_mapping(v) for v in response.data]

    def list_by_provider(self, provider: str) -> list[VenueMapping]:
        """List all venues for a specific provider."""
        # Get venue_ids for this provider
        provider_response = (
            get_client()
            .table("venue_providers")
            .select("venue_id, provider, external_id")
            .eq("provider", provider)
            .execute()
        )

        if not provider_response.data:
            return []

        venue_ids = [p["venue_id"] for p in provider_response.data]
        provider_map = {p["venue_id"]: p for p in provider_response.data}

        # Get venue details
        venues_response = (
            get_client()
            .table("venues")
            .select("*")
            .in_("venue_id", venue_ids)
            .execute()
        )

        return [
            self._row_to_mapping(v, provider_map.get(v["venue_id"]))
            for v in venues_response.data
        ]

    def count(self) -> int:
        """Get total number of venues in registry."""
        response = (
            get_client()
            .table("venues")
            .select("*", count="exact")
            .execute()
        )
        return response.count or 0
