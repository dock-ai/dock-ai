-- Restaurant mappings table
-- Maps restaurants to their booking providers (Zenchef, Planity, TheFork, etc.)

CREATE TABLE IF NOT EXISTS restaurant_mappings (
    id BIGSERIAL PRIMARY KEY,
    restaurant_id TEXT UNIQUE NOT NULL,
    provider TEXT NOT NULL,
    external_id TEXT NOT NULL,
    name TEXT NOT NULL,
    domain TEXT,
    city TEXT,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- Indexes for common queries
CREATE INDEX IF NOT EXISTS idx_restaurant_mappings_provider ON restaurant_mappings(provider);
CREATE INDEX IF NOT EXISTS idx_restaurant_mappings_domain ON restaurant_mappings(domain);
CREATE INDEX IF NOT EXISTS idx_restaurant_mappings_city ON restaurant_mappings(city);

-- Enable Row Level Security (RLS)
ALTER TABLE restaurant_mappings ENABLE ROW LEVEL SECURITY;

-- Policy: Allow public read access (restaurants are public data)
CREATE POLICY "Allow public read access"
    ON restaurant_mappings
    FOR SELECT
    USING (true);

-- Policy: Only authenticated users with admin role can insert/update/delete
-- (You'll need to set up authentication for write operations)
CREATE POLICY "Allow admin write access"
    ON restaurant_mappings
    FOR ALL
    USING (auth.jwt() ->> 'role' = 'admin');

-- Function to auto-update updated_at timestamp
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

-- Trigger to call the function on update
CREATE TRIGGER update_restaurant_mappings_updated_at
    BEFORE UPDATE ON restaurant_mappings
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at_column();
