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

Create a new file in `src/dock_ai/adapters/`:

```python
# src/dock_ai/adapters/your_provider.py
"""Your Provider booking adapter."""

import os
import httpx
from .base import BaseAdapter, Venue, TimeSlot, Booking


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
    ) -> list[Venue]:
        """Search for venues."""
        # If no API key, return mock data for testing
        if not self.api_key:
            return self._mock_search(city, date, party_size, cuisine)

        # Real API call
        response = await self.client.get(
            "/venues",
            params={"city": city, "date": date, "party_size": party_size}
        )
        response.raise_for_status()
        data = response.json()

        return [
            Venue(
                id=v["id"],
                name=v["name"],
                address=v["address"],
                cuisine=v.get("cuisine", "Unknown"),
                provider=self.provider_name,
                rating=v.get("rating"),
            )
            for v in data["venues"]
        ]

    def _mock_search(self, city: str, date: str, party_size: int, cuisine: str | None) -> list[Venue]:
        """Return mock data for testing without API key."""
        return [
            Venue(
                id="your_provider_test_001",
                name="Test Venue",
                address="123 Test Street",
                cuisine="French",
                provider=self.provider_name,
                rating=4.5,
            )
        ]

    # ... implement other methods (get_availability, book, cancel)
```

### Step 2: Register the Adapter

Update `src/dock_ai/adapters/__init__.py`:

```python
from .base import BaseAdapter, Venue, TimeSlot, Booking
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
from dock_ai.adapters.your_provider import YourProviderAdapter

@pytest.mark.asyncio
async def test_search_mock_mode():
    """Test search works in mock mode (no API key)."""
    adapter = YourProviderAdapter()
    results = await adapter.search("Paris", "2025-01-15", 4)
    assert len(results) > 0
    assert results[0].provider == "your_provider"

@pytest.mark.asyncio
async def test_search_returns_venue_objects():
    """Test that search returns proper Venue objects."""
    adapter = YourProviderAdapter()
    results = await adapter.search("Paris", "2025-01-15", 2)
    for v in results:
        assert v.id is not None
        assert v.name is not None
        assert v.provider == "your_provider"
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

    async def search(self, city, date, party_size, cuisine=None) -> list[Venue]
    async def get_availability(self, venue_id, date, party_size) -> list[TimeSlot]
    async def book(self, venue_id, date, time, party_size, customer_name, customer_email, customer_phone) -> Booking
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
