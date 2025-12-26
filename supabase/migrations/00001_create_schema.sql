-- Dock AI Database Schema
-- Multi-category booking aggregator

-- ============================================================================
-- VENUES TABLE
-- ============================================================================
-- Main venue registry (restaurants, hair salons, spas, fitness centers)

CREATE TABLE IF NOT EXISTS venues (
    id BIGSERIAL PRIMARY KEY,
    venue_id TEXT UNIQUE NOT NULL,           -- Our internal ID
    name TEXT NOT NULL,
    category TEXT NOT NULL,                   -- restaurant, hair_salon, spa, fitness
    address TEXT,
    city TEXT,
    country TEXT DEFAULT 'FR',
    domain TEXT,                              -- Website domain for entity-card lookup
    metadata JSONB DEFAULT '{}',              -- Category-specific info (cuisine, services, etc.)
    status TEXT DEFAULT 'active',             -- active, inactive, pending
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- Indexes
CREATE INDEX IF NOT EXISTS idx_venues_category ON venues(category);
CREATE INDEX IF NOT EXISTS idx_venues_city ON venues(city);
CREATE INDEX IF NOT EXISTS idx_venues_domain ON venues(domain);
CREATE INDEX IF NOT EXISTS idx_venues_status ON venues(status);

-- ============================================================================
-- VENUE_PROVIDERS TABLE
-- ============================================================================
-- Maps venues to their booking providers (one venue can be on multiple platforms)

CREATE TABLE IF NOT EXISTS venue_providers (
    id BIGSERIAL PRIMARY KEY,
    venue_id TEXT NOT NULL REFERENCES venues(venue_id) ON DELETE CASCADE,
    provider TEXT NOT NULL,                   -- demo, zenchef, planity, etc.
    external_id TEXT NOT NULL,                -- ID in the provider's system
    credentials JSONB DEFAULT '{}',           -- Encrypted API keys (if needed)
    sync_status TEXT DEFAULT 'active',        -- active, paused, error
    last_synced_at TIMESTAMPTZ,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW(),
    UNIQUE(venue_id, provider)                -- One entry per venue-provider pair
);

-- Indexes
CREATE INDEX IF NOT EXISTS idx_venue_providers_provider ON venue_providers(provider);
CREATE INDEX IF NOT EXISTS idx_venue_providers_venue_id ON venue_providers(venue_id);

-- ============================================================================
-- BOOKINGS TABLE
-- ============================================================================
-- All bookings made through Dock AI (for history and analytics)

CREATE TABLE IF NOT EXISTS bookings (
    id BIGSERIAL PRIMARY KEY,
    booking_id TEXT UNIQUE NOT NULL,          -- Our internal booking ID
    venue_id TEXT NOT NULL REFERENCES venues(venue_id),
    provider TEXT NOT NULL,                    -- Which provider processed this
    provider_booking_id TEXT,                  -- ID in the provider's system
    category TEXT NOT NULL,
    params JSONB NOT NULL,                     -- date, time, party_size, service, etc.
    customer_name TEXT NOT NULL,
    customer_email TEXT NOT NULL,
    customer_phone TEXT,
    status TEXT DEFAULT 'confirmed',           -- confirmed, cancelled, completed, no_show
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- Indexes
CREATE INDEX IF NOT EXISTS idx_bookings_venue_id ON bookings(venue_id);
CREATE INDEX IF NOT EXISTS idx_bookings_customer_email ON bookings(customer_email);
CREATE INDEX IF NOT EXISTS idx_bookings_status ON bookings(status);
CREATE INDEX IF NOT EXISTS idx_bookings_created_at ON bookings(created_at);

-- ============================================================================
-- ROW LEVEL SECURITY
-- ============================================================================

ALTER TABLE venues ENABLE ROW LEVEL SECURITY;
ALTER TABLE venue_providers ENABLE ROW LEVEL SECURITY;
ALTER TABLE bookings ENABLE ROW LEVEL SECURITY;

-- Public read access for venues
CREATE POLICY "Public read venues" ON venues FOR SELECT USING (true);

-- Public read access for venue_providers (needed for lookups)
CREATE POLICY "Public read venue_providers" ON venue_providers FOR SELECT USING (true);

-- Bookings: users can only see their own bookings (by email)
-- For now, allow all reads (we'll add proper auth later)
CREATE POLICY "Read own bookings" ON bookings FOR SELECT USING (true);

-- Admin write access
CREATE POLICY "Admin write venues" ON venues FOR ALL
    USING (auth.jwt() ->> 'role' = 'admin');
CREATE POLICY "Admin write venue_providers" ON venue_providers FOR ALL
    USING (auth.jwt() ->> 'role' = 'admin');
CREATE POLICY "Admin write bookings" ON bookings FOR ALL
    USING (auth.jwt() ->> 'role' = 'admin');

-- Service role can insert bookings (for MCP server)
CREATE POLICY "Service insert bookings" ON bookings FOR INSERT
    WITH CHECK (true);
CREATE POLICY "Service update bookings" ON bookings FOR UPDATE
    USING (true);

-- ============================================================================
-- TRIGGERS
-- ============================================================================

CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER update_venues_updated_at
    BEFORE UPDATE ON venues
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_venue_providers_updated_at
    BEFORE UPDATE ON venue_providers
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_bookings_updated_at
    BEFORE UPDATE ON bookings
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();
