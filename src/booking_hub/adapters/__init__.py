"""Restaurant booking provider adapters."""

from .base import BaseAdapter, Restaurant, TimeSlot, Booking
from .zenchef import ZenchefAdapter


def get_adapter_for_provider(provider: str, **kwargs) -> BaseAdapter:
    """
    Get an adapter instance for a booking provider.

    Args:
        provider: Provider name (e.g., "zenchef", "planity")
        **kwargs: Additional arguments to pass to the adapter constructor

    Returns:
        Adapter instance for the specified provider

    Raises:
        ValueError: If the provider is not supported
    """
    adapters = {
        "zenchef": ZenchefAdapter,
        # Add more providers here as they're implemented
        # "planity": PlanityAdapter,
        # "resy": ResyAdapter,
        # "opentable": OpenTableAdapter,
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
    "Restaurant",
    "TimeSlot",
    "Booking",
    "ZenchefAdapter",
    "get_adapter_for_provider",
]
