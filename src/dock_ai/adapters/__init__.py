"""Booking provider adapters."""

from .base import BaseAdapter, Venue, TimeSlot, Booking
from .demo import DemoAdapter


def get_adapter_for_provider(provider: str, **kwargs) -> BaseAdapter:
    """
    Get an adapter instance for a booking provider.

    Args:
        provider: Provider name (e.g., "demo", "your_provider")
        **kwargs: Additional arguments to pass to the adapter constructor

    Returns:
        Adapter instance for the specified provider

    Raises:
        ValueError: If the provider is not supported
    """
    adapters = {
        "demo": DemoAdapter,
        # Add your provider adapters here:
        # "your_provider": YourProviderAdapter,
    }

    adapter_class = adapters.get(provider.lower())
    if not adapter_class:
        supported = ", ".join(adapters.keys())
        raise ValueError(
            f"Unsupported provider: {provider}. "
            f"Supported providers: {supported}"
        )

    return adapter_class(**kwargs)


__all__ = [
    "BaseAdapter",
    "Venue",
    "TimeSlot",
    "Booking",
    "DemoAdapter",
    "get_adapter_for_provider",
]
