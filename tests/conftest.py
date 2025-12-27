"""Pytest configuration and fixtures."""

import os
from unittest.mock import MagicMock, patch

import pytest


def create_mock_supabase_client():
    """Create a mock Supabase client."""
    mock_client = MagicMock()

    # Mock table queries to return empty results by default
    mock_response = MagicMock()
    mock_response.data = []
    mock_response.count = 0

    mock_query = MagicMock()
    mock_query.select.return_value = mock_query
    mock_query.insert.return_value = mock_query
    mock_query.update.return_value = mock_query
    mock_query.eq.return_value = mock_query
    mock_query.ilike.return_value = mock_query
    mock_query.in_.return_value = mock_query
    mock_query.limit.return_value = mock_query
    mock_query.order.return_value = mock_query
    mock_query.execute.return_value = mock_response

    mock_client.table.return_value = mock_query

    return mock_client


# Create the mock at module level
_mock_client = create_mock_supabase_client()


@pytest.fixture(autouse=True)
def mock_supabase(monkeypatch):
    """Mock Supabase client for all tests."""
    # Clear the lru_cache
    from dock_ai.registry import database
    database.get_supabase_client.cache_clear()

    # Set fake environment variables
    monkeypatch.setenv("SUPABASE_URL", "https://fake.supabase.co")
    monkeypatch.setenv("SUPABASE_KEY", "fake-key")

    # Patch the supabase.create_client function
    with patch("dock_ai.registry.database.create_client", return_value=_mock_client):
        yield _mock_client

    # Clear cache after test
    database.get_supabase_client.cache_clear()


@pytest.fixture
def mock_supabase_with_venues(mock_supabase):
    """Mock Supabase with sample venue data."""
    venue_data = [
        {
            "venue_id": "demo_paris_001",
            "name": "The Golden Fork",
            "category": "restaurant",
            "address": "15 Avenue des Champs",
            "city": "Paris",
            "country": "FR",
            "domain": "goldenfork.example.com",
            "metadata": {"cuisine": "French"},
        }
    ]

    provider_data = [
        {
            "venue_id": "demo_paris_001",
            "provider": "demo",
            "external_id": "ext_001",
        }
    ]

    # Configure mock to return venue data
    def mock_execute():
        response = MagicMock()
        response.data = venue_data
        response.count = 1
        return response

    mock_supabase.table.return_value.select.return_value.eq.return_value.execute = mock_execute

    return mock_supabase
