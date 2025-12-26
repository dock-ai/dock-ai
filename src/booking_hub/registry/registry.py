"""Restaurant registry for mapping restaurants to their booking providers."""

from pydantic import BaseModel

from .database import get_client


class RestaurantMapping(BaseModel):
    """Maps a restaurant to its booking provider."""

    restaurant_id: str
    provider: str  # "zenchef", "planity", "thefork"
    external_id: str  # ID in the provider's system
    name: str
    domain: str | None = None  # e.g. "lepetitparis.com"
    city: str | None = None


class Registry:
    """
    Maps restaurant IDs to their booking providers.
    Uses Supabase for persistent storage.
    """

    TABLE = "restaurant_mappings"

    def _row_to_mapping(self, row: dict) -> RestaurantMapping:
        """Convert a database row to RestaurantMapping."""
        return RestaurantMapping(
            restaurant_id=row["restaurant_id"],
            provider=row["provider"],
            external_id=row["external_id"],
            name=row["name"],
            domain=row.get("domain"),
            city=row.get("city"),
        )

    def get_provider(self, restaurant_id: str) -> str | None:
        """Get the provider for a restaurant."""
        response = (
            get_client()
            .table(self.TABLE)
            .select("provider")
            .eq("restaurant_id", restaurant_id)
            .execute()
        )
        if response.data:
            return response.data[0]["provider"]
        return None

    def get_mapping(self, restaurant_id: str) -> RestaurantMapping | None:
        """Get full mapping for a restaurant."""
        response = (
            get_client()
            .table(self.TABLE)
            .select("*")
            .eq("restaurant_id", restaurant_id)
            .execute()
        )
        if response.data:
            return self._row_to_mapping(response.data[0])
        return None

    def register(self, mapping: RestaurantMapping) -> None:
        """Register a new restaurant mapping."""
        get_client().table(self.TABLE).upsert(
            {
                "restaurant_id": mapping.restaurant_id,
                "provider": mapping.provider,
                "external_id": mapping.external_id,
                "name": mapping.name,
                "domain": mapping.domain,
                "city": mapping.city,
            }
        ).execute()

    def find_by_domain(self, domain: str) -> RestaurantMapping | None:
        """Find a restaurant by its website domain (for entity-card concept)."""
        # Normalize domain
        normalized = domain.lower().strip()
        normalized = normalized.replace("http://", "").replace("https://", "")
        normalized = normalized.replace("www.", "").rstrip("/")

        # Query with ILIKE for case-insensitive matching
        response = (
            get_client()
            .table(self.TABLE)
            .select("*")
            .ilike("domain", f"%{normalized}%")
            .execute()
        )

        # Double-check with exact normalized comparison
        for row in response.data:
            if row.get("domain"):
                db_domain = row["domain"].lower().replace("www.", "").rstrip("/")
                if normalized == db_domain:
                    return self._row_to_mapping(row)

        return None

    def list_all(self) -> list[RestaurantMapping]:
        """List all registered restaurants."""
        response = get_client().table(self.TABLE).select("*").execute()
        return [self._row_to_mapping(row) for row in response.data]

    def list_by_provider(self, provider: str) -> list[RestaurantMapping]:
        """List all restaurants for a specific provider."""
        response = (
            get_client()
            .table(self.TABLE)
            .select("*")
            .eq("provider", provider)
            .execute()
        )
        return [self._row_to_mapping(row) for row in response.data]

    def list_by_city(self, city: str) -> list[RestaurantMapping]:
        """List all restaurants in a specific city."""
        response = (
            get_client()
            .table(self.TABLE)
            .select("*")
            .ilike("city", city)
            .execute()
        )
        return [self._row_to_mapping(row) for row in response.data]

    def remove(self, restaurant_id: str) -> bool:
        """Remove a restaurant mapping."""
        response = (
            get_client()
            .table(self.TABLE)
            .delete()
            .eq("restaurant_id", restaurant_id)
            .execute()
        )
        return len(response.data) > 0

    def count(self) -> int:
        """Get total number of restaurants in registry."""
        response = (
            get_client()
            .table(self.TABLE)
            .select("*", count="exact")
            .execute()
        )
        return response.count or 0
