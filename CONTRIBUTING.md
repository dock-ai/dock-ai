# Contributing to Dock AI

Thank you for your interest in contributing to Dock AI! This guide will help you get started.

## Ways to Contribute

1. **Add a new booking provider adapter** (most impactful)
2. Report bugs or request features via GitHub Issues
3. Improve documentation
4. Fix bugs or implement features

## Adding a New Adapter

This is the most valuable contribution you can make. Here's how to add support for a new booking platform.

### Step 1: Create the Adapter File

Create a new file in `src/booking_hub/adapters/`:

```python
# src/booking_hub/adapters/your_provider.py
"""Your Provider booking adapter."""

import os
import httpx
from .base import BaseAdapter, Restaurant, TimeSlot, Booking


class YourProviderAdapter(BaseAdapter):
    """Your Provider booking adapter."""

    provider_name = "your_provider"

    def __init__(self):
        self.api_key = os.environ.get("YOUR_PROVIDER_API_KEY")
        self.base_url = "https://api.yourprovider.com/v1"
        self.client = httpx.AsyncClient(
            base_url=self.base_url,
            headers={"Authorization": f"Bearer {self.api_key}"} if self.api_key else {}
        )

    async def search(
        self,
        city: str,
        date: str,
        party_size: int,
        cuisine: str | None = None
    ) -> list[Restaurant]:
        """Search for restaurants."""
        # If no API key, return mock data for testing
        if not self.api_key:
            return self._mock_search(city, date, party_size, cuisine)

        # Real API call
        response = await self.client.get(
            "/restaurants",
            params={"city": city, "date": date, "party_size": party_size}
        )
        response.raise_for_status()
        data = response.json()

        return [
            Restaurant(
                id=r["id"],
                name=r["name"],
                address=r["address"],
                cuisine=r.get("cuisine", "Unknown"),
                provider=self.provider_name,
                rating=r.get("rating"),
            )
            for r in data["restaurants"]
        ]

    def _mock_search(self, city: str, date: str, party_size: int, cuisine: str | None) -> list[Restaurant]:
        """Return mock data for testing without API key."""
        return [
            Restaurant(
                id="your_provider_test_001",
                name="Test Restaurant",
                address="123 Test Street",
                cuisine="French",
                provider=self.provider_name,
                rating=4.5,
            )
        ]

    # ... implement other methods (get_availability, book, cancel)
```

### Step 2: Register the Adapter

Update `src/booking_hub/adapters/__init__.py`:

```python
from .base import BaseAdapter, Restaurant, TimeSlot, Booking
from .demo import DemoAdapter
from .your_provider import YourProviderAdapter  # Add this

_adapters = {
    "demo": DemoAdapter,
    "your_provider": YourProviderAdapter,  # Add this
}

def get_adapter_for_provider(provider: str) -> BaseAdapter:
    adapter_class = _adapters.get(provider)
    if adapter_class:
        return adapter_class()
    raise ValueError(f"Unknown provider: {provider}")
```

### Step 3: Add Tests

Create `tests/adapters/test_your_provider.py`:

```python
import pytest
from booking_hub.adapters.your_provider import YourProviderAdapter

@pytest.mark.asyncio
async def test_search_mock_mode():
    """Test search works in mock mode (no API key)."""
    adapter = YourProviderAdapter()
    results = await adapter.search("Paris", "2025-01-15", 4)
    assert len(results) > 0
    assert results[0].provider == "your_provider"

@pytest.mark.asyncio
async def test_search_returns_restaurant_objects():
    """Test that search returns proper Restaurant objects."""
    adapter = YourProviderAdapter()
    results = await adapter.search("Paris", "2025-01-15", 2)
    for r in results:
        assert r.id is not None
        assert r.name is not None
        assert r.provider == "your_provider"
```

### Step 4: Document Environment Variables

Add to `.env.example`:

```bash
# Your Provider API (optional - runs in mock mode without)
YOUR_PROVIDER_API_KEY=
```

### Step 5: Submit a Pull Request

1. Fork the repository
2. Create a feature branch: `git checkout -b add-your-provider-adapter`
3. Make your changes
4. Run tests: `pytest`
5. Commit: `git commit -m "Add YourProvider adapter"`
6. Push: `git push origin add-your-provider-adapter`
7. Open a Pull Request

## Adapter Interface

All adapters must implement the `BaseAdapter` interface:

```python
class BaseAdapter(ABC):
    provider_name: str

    async def search(self, city, date, party_size, cuisine=None) -> list[Restaurant]
    async def get_availability(self, restaurant_id, date, party_size) -> list[TimeSlot]
    async def book(self, restaurant_id, date, time, party_size, customer_name, customer_email, customer_phone) -> Booking
    async def cancel(self, booking_id) -> bool
```

## Mock Mode vs Production Mode

Adapters should work in two modes:

1. **Mock Mode** (no API key): Return realistic fake data for testing
2. **Production Mode** (with API key): Call the real API

This allows contributors to develop and test without needing API access.

## Code Style

- Use Python 3.10+ type hints
- Follow PEP 8 guidelines
- Use `async/await` for all I/O operations
- Add docstrings to all public methods
- Write tests for new functionality

## Questions?

Open an issue on GitHub or reach out to the maintainers.
