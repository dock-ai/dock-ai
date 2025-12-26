-- Seed data for testing and development
-- These are example restaurants to demonstrate the system

INSERT INTO restaurant_mappings (restaurant_id, provider, external_id, name, domain, city)
VALUES
    -- Paris restaurants
    ('rest_paris_001', 'zenchef', 'zc_lepetitparis_001', 'Le Petit Paris', 'lepetitparis.fr', 'Paris'),
    ('rest_paris_002', 'zenchef', 'zc_latoureiffel_002', 'La Tour Eiffel Bistro', 'latoureiffelbistro.com', 'Paris'),
    ('rest_paris_003', 'zenchef', 'zc_sakurahouse_003', 'Sakura House', 'sakurahouse-paris.fr', 'Paris'),
    ('rest_paris_004', 'zenchef', 'zc_labelleassiette_004', 'La Belle Assiette', NULL, 'Paris'),
    -- Lyon restaurants
    ('rest_lyon_001', 'zenchef', 'zc_bouchonlyonnais_001', 'Le Bouchon Lyonnais', 'bouchonlyonnais.fr', 'Lyon'),
    ('rest_lyon_002', 'zenchef', 'zc_chezpaul_002', 'Chez Paul', NULL, 'Lyon'),
    ('rest_lyon_003', 'zenchef', 'zc_trattorialyon_003', 'Trattoria Lyon', 'trattoria-lyon.com', 'Lyon'),
    -- Marseille restaurants
    ('rest_marseille_001', 'zenchef', 'zc_levieuxport_001', 'Le Vieux Port', 'vieuxport-restaurant.fr', 'Marseille'),
    ('rest_marseille_002', 'zenchef', 'zc_bouillabaisseor_002', 'Bouillabaisse d''Or', 'bouillabaissedor.com', 'Marseille'),
    ('rest_marseille_003', 'zenchef', 'zc_lamaisonbleue_003', 'La Maison Bleue', NULL, 'Marseille')
ON CONFLICT (restaurant_id) DO NOTHING;
