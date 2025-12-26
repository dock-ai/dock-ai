-- Seed data for testing and development
-- These are example venues to demonstrate the system

INSERT INTO restaurant_mappings (restaurant_id, provider, external_id, name, domain, city)
VALUES
    -- Paris venues
    ('demo_paris_001', 'demo', 'ext_goldenfork_001', 'The Golden Fork', 'goldenfork.example.com', 'Paris'),
    ('demo_paris_002', 'demo', 'ext_urbangarden_002', 'Urban Garden', 'urbangarden.example.com', 'Paris'),
    ('demo_paris_003', 'demo', 'ext_sakurablossom_003', 'Sakura Blossom', 'sakurablossom.example.com', 'Paris'),
    ('demo_paris_004', 'demo', 'ext_blueoyster_004', 'The Blue Oyster', NULL, 'Paris'),
    -- London venues
    ('demo_london_001', 'demo', 'ext_gildedplate_001', 'The Gilded Plate', 'gildedplate.example.com', 'London'),
    ('demo_london_002', 'demo', 'ext_spiceroute_002', 'Spice Route', NULL, 'London'),
    ('demo_london_003', 'demo', 'ext_greentable_003', 'The Green Table', 'greentable.example.com', 'London'),
    -- New York venues
    ('demo_nyc_001', 'demo', 'ext_manhattannights_001', 'Manhattan Nights', 'manhattannights.example.com', 'New York'),
    ('demo_nyc_002', 'demo', 'ext_littleitaly_002', 'Little Italy Kitchen', 'littleitalykitchen.example.com', 'New York'),
    ('demo_nyc_003', 'demo', 'ext_harlemsoul_003', 'Harlem Soul', NULL, 'New York')
ON CONFLICT (restaurant_id) DO NOTHING;
