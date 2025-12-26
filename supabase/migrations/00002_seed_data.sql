-- Seed data for testing and development

-- ============================================================================
-- VENUES
-- ============================================================================

INSERT INTO venues (venue_id, name, category, address, city, country, domain, metadata) VALUES
    -- Paris Restaurants
    ('demo_paris_001', 'The Golden Fork', 'restaurant', '15 Avenue des Champs, 75008 Paris', 'Paris', 'FR', 'goldenfork.example.com', '{"cuisine": "French", "price_range": "$$$"}'),
    ('demo_paris_002', 'Urban Garden', 'restaurant', '42 Rue de Rivoli, 75001 Paris', 'Paris', 'FR', 'urbangarden.example.com', '{"cuisine": "Contemporary", "price_range": "$$"}'),
    ('demo_paris_003', 'Sakura Blossom', 'restaurant', '8 Rue Saint-Anne, 75001 Paris', 'Paris', 'FR', 'sakurablossom.example.com', '{"cuisine": "Japanese", "price_range": "$$$"}'),
    ('demo_paris_004', 'The Blue Oyster', 'restaurant', '23 Boulevard Saint-Germain, 75005 Paris', 'Paris', 'FR', NULL, '{"cuisine": "Seafood", "price_range": "$$$$"}'),

    -- London Restaurants
    ('demo_london_001', 'The Gilded Plate', 'restaurant', '127 Kensington High Street, London W8', 'London', 'UK', 'gildedplate.example.com', '{"cuisine": "British", "price_range": "$$$$"}'),
    ('demo_london_002', 'Spice Route', 'restaurant', '45 Brick Lane, London E1', 'London', 'UK', NULL, '{"cuisine": "Indian", "price_range": "$$"}'),
    ('demo_london_003', 'The Green Table', 'restaurant', '88 Borough Market, London SE1', 'London', 'UK', 'greentable.example.com', '{"cuisine": "Vegetarian", "price_range": "$$"}'),

    -- New York Restaurants
    ('demo_nyc_001', 'Manhattan Nights', 'restaurant', '350 5th Avenue, New York, NY 10118', 'New York', 'US', 'manhattannights.example.com', '{"cuisine": "American", "price_range": "$$$"}'),
    ('demo_nyc_002', 'Little Italy Kitchen', 'restaurant', '156 Mulberry Street, New York, NY 10013', 'New York', 'US', 'littleitalykitchen.example.com', '{"cuisine": "Italian", "price_range": "$$"}'),
    ('demo_nyc_003', 'Harlem Soul', 'restaurant', '2340 Frederick Douglass Blvd, New York, NY 10027', 'New York', 'US', NULL, '{"cuisine": "Soul Food", "price_range": "$$"}'),

    -- Paris Hair Salons
    ('demo_paris_hair_001', 'Salon Chic', 'hair_salon', '10 Rue du Faubourg, 75008 Paris', 'Paris', 'FR', 'salonchic.example.com', '{"services": ["Haircut", "Coloring", "Styling"]}'),
    ('demo_paris_hair_002', 'Cut & Color Studio', 'hair_salon', '55 Avenue Montaigne, 75008 Paris', 'Paris', 'FR', NULL, '{"services": ["Coloring", "Balayage", "Highlights"]}'),

    -- London Hair Salons
    ('demo_london_hair_001', 'Blade & Fade', 'hair_salon', '22 Soho Square, London W1', 'London', 'UK', 'bladeandfade.example.com', '{"services": ["Haircut", "Beard Trim", "Styling"]}'),

    -- Paris Spas
    ('demo_paris_spa_001', 'Zen Retreat', 'spa', '18 Place Vendome, 75001 Paris', 'Paris', 'FR', 'zenretreat.example.com', '{"services": ["Massage", "Facial", "Body Treatment"]}')
ON CONFLICT (venue_id) DO NOTHING;

-- ============================================================================
-- VENUE PROVIDERS
-- ============================================================================

INSERT INTO venue_providers (venue_id, provider, external_id) VALUES
    -- All venues use demo provider for now
    ('demo_paris_001', 'demo', 'ext_goldenfork_001'),
    ('demo_paris_002', 'demo', 'ext_urbangarden_002'),
    ('demo_paris_003', 'demo', 'ext_sakurablossom_003'),
    ('demo_paris_004', 'demo', 'ext_blueoyster_004'),
    ('demo_london_001', 'demo', 'ext_gildedplate_001'),
    ('demo_london_002', 'demo', 'ext_spiceroute_002'),
    ('demo_london_003', 'demo', 'ext_greentable_003'),
    ('demo_nyc_001', 'demo', 'ext_manhattannights_001'),
    ('demo_nyc_002', 'demo', 'ext_littleitaly_002'),
    ('demo_nyc_003', 'demo', 'ext_harlemsoul_003'),
    ('demo_paris_hair_001', 'demo', 'ext_salonchic_001'),
    ('demo_paris_hair_002', 'demo', 'ext_cutcolor_002'),
    ('demo_london_hair_001', 'demo', 'ext_bladefade_001'),
    ('demo_paris_spa_001', 'demo', 'ext_zenretreat_001')
ON CONFLICT (venue_id, provider) DO NOTHING;
