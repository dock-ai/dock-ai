"""Seed data for restaurant registry.

This data is used for:
- Initial database seeding
- Testing and development
- Documentation examples

To seed the database, run the SQL migration in supabase/migrations/
or use the seed script: python -m booking_hub.scripts.seed
"""

SEED_RESTAURANTS = [
    # Paris restaurants
    {
        "restaurant_id": "rest_paris_001",
        "provider": "zenchef",
        "external_id": "zc_lepetitparis_001",
        "name": "Le Petit Paris",
        "domain": "lepetitparis.fr",
        "city": "Paris",
    },
    {
        "restaurant_id": "rest_paris_002",
        "provider": "zenchef",
        "external_id": "zc_latoureiffel_002",
        "name": "La Tour Eiffel Bistro",
        "domain": "latoureiffelbistro.com",
        "city": "Paris",
    },
    {
        "restaurant_id": "rest_paris_003",
        "provider": "zenchef",
        "external_id": "zc_sakurahouse_003",
        "name": "Sakura House",
        "domain": "sakurahouse-paris.fr",
        "city": "Paris",
    },
    {
        "restaurant_id": "rest_paris_004",
        "provider": "zenchef",
        "external_id": "zc_labelleassiette_004",
        "name": "La Belle Assiette",
        "domain": None,
        "city": "Paris",
    },
    # Lyon restaurants
    {
        "restaurant_id": "rest_lyon_001",
        "provider": "zenchef",
        "external_id": "zc_bouchonlyonnais_001",
        "name": "Le Bouchon Lyonnais",
        "domain": "bouchonlyonnais.fr",
        "city": "Lyon",
    },
    {
        "restaurant_id": "rest_lyon_002",
        "provider": "zenchef",
        "external_id": "zc_chezpaul_002",
        "name": "Chez Paul",
        "domain": None,
        "city": "Lyon",
    },
    {
        "restaurant_id": "rest_lyon_003",
        "provider": "zenchef",
        "external_id": "zc_trattorialyon_003",
        "name": "Trattoria Lyon",
        "domain": "trattoria-lyon.com",
        "city": "Lyon",
    },
    # Marseille restaurants
    {
        "restaurant_id": "rest_marseille_001",
        "provider": "zenchef",
        "external_id": "zc_levieuxport_001",
        "name": "Le Vieux Port",
        "domain": "vieuxport-restaurant.fr",
        "city": "Marseille",
    },
    {
        "restaurant_id": "rest_marseille_002",
        "provider": "zenchef",
        "external_id": "zc_bouillabaisseor_002",
        "name": "Bouillabaisse d'Or",
        "domain": "bouillabaissedor.com",
        "city": "Marseille",
    },
    {
        "restaurant_id": "rest_marseille_003",
        "provider": "zenchef",
        "external_id": "zc_lamaisonbleue_003",
        "name": "La Maison Bleue",
        "domain": None,
        "city": "Marseille",
    },
]
