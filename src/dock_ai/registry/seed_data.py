"""Seed data for venue registry.

This data is used for:
- Initial database seeding
- Testing and development
- Documentation examples

To seed the database, run the SQL migration in supabase/migrations/
"""

SEED_VENUES = [
    # Paris venues
    {
        "venue_id": "demo_paris_001",
        "provider": "demo",
        "external_id": "ext_goldenfork_001",
        "name": "The Golden Fork",
        "domain": "goldenfork.example.com",
        "city": "Paris",
    },
    {
        "venue_id": "demo_paris_002",
        "provider": "demo",
        "external_id": "ext_urbangarden_002",
        "name": "Urban Garden",
        "domain": "urbangarden.example.com",
        "city": "Paris",
    },
    {
        "venue_id": "demo_paris_003",
        "provider": "demo",
        "external_id": "ext_sakurablossom_003",
        "name": "Sakura Blossom",
        "domain": "sakurablossom.example.com",
        "city": "Paris",
    },
    {
        "venue_id": "demo_paris_004",
        "provider": "demo",
        "external_id": "ext_blueoyster_004",
        "name": "The Blue Oyster",
        "domain": None,
        "city": "Paris",
    },
    # London venues
    {
        "venue_id": "demo_london_001",
        "provider": "demo",
        "external_id": "ext_gildedplate_001",
        "name": "The Gilded Plate",
        "domain": "gildedplate.example.com",
        "city": "London",
    },
    {
        "venue_id": "demo_london_002",
        "provider": "demo",
        "external_id": "ext_spiceroute_002",
        "name": "Spice Route",
        "domain": None,
        "city": "London",
    },
    {
        "venue_id": "demo_london_003",
        "provider": "demo",
        "external_id": "ext_greentable_003",
        "name": "The Green Table",
        "domain": "greentable.example.com",
        "city": "London",
    },
    # New York venues
    {
        "venue_id": "demo_nyc_001",
        "provider": "demo",
        "external_id": "ext_manhattannights_001",
        "name": "Manhattan Nights",
        "domain": "manhattannights.example.com",
        "city": "New York",
    },
    {
        "venue_id": "demo_nyc_002",
        "provider": "demo",
        "external_id": "ext_littleitaly_002",
        "name": "Little Italy Kitchen",
        "domain": "littleitalykitchen.example.com",
        "city": "New York",
    },
    {
        "venue_id": "demo_nyc_003",
        "provider": "demo",
        "external_id": "ext_harlemsoul_003",
        "name": "Harlem Soul",
        "domain": None,
        "city": "New York",
    },
]
