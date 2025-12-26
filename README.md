# Dock AI

An MCP server that aggregates multiple booking platforms behind a unified interface.

```
┌─────────────────────────────────────────────────────────────────┐
│  AI Agent (Claude, GPT, etc.)                                   │
│  "Book a table for 4 at a French restaurant tonight"            │
└─────────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────────┐
│  DOCK-AI MCP                                                    │
│                                                                 │
│  Tools:                                                         │
│  ├── get_filters             - Get filters for a category      │
│  ├── search_venues           - Search venues by category/city  │
│  ├── check_availability      - Check available time slots      │
│  ├── book                    - Make a reservation              │
│  ├── cancel                  - Cancel a reservation            │
│  └── find_venue_by_domain    - Find by website                 │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
                              │
        ┌─────────────────────┼─────────────────────┐
        ▼                     ▼                     ▼
   ┌──────────┐         ┌──────────┐         ┌──────────┐
   │ Provider │         │ Provider │         │ Provider │
   │    A     │         │    B     │         │    C     │
   └──────────┘         └──────────┘         └──────────┘
```

## Quick Start

### 1. Clone and Install

```bash
git clone https://github.com/dock-ai/dock-ai.git
cd dock-ai

# Create virtual environment
python3 -m venv .venv
source .venv/bin/activate

# Install dependencies
pip install -e .
```

### 2. Set Up Supabase

1. Create a free project at [supabase.com](https://supabase.com)
2. Run the migrations in `supabase/migrations/` via the SQL editor
3. Copy `.env.example` to `.env` and add your Supabase credentials

```bash
cp .env.example .env
# Edit .env with your SUPABASE_URL and SUPABASE_KEY
```

### 3. Configure Claude Desktop

Add to `~/Library/Application Support/Claude/claude_desktop_config.json`:

```json
{
  "mcpServers": {
    "dock-ai": {
      "command": "/path/to/dock-ai/.venv/bin/python",
      "args": ["-m", "dock_ai.server"],
      "cwd": "/path/to/dock-ai",
      "env": {
        "PYTHONPATH": "/path/to/dock-ai/src",
        "SUPABASE_URL": "https://your-project.supabase.co",
        "SUPABASE_KEY": "your-key"
      }
    }
  }
}
```

### 4. Test It

Restart Claude Desktop and try:

> "Search for venues in Paris for 4 people on January 15th"

## Available Tools

### `get_filters`

Get required parameters for a category and tool. **Call this before each tool!**

```python
# Search filters for restaurants
get_filters(category="restaurant", tool="search")
# → {"cuisine": ["French", ...], "price_range": ["$", ...]}

# Booking params for restaurants (has party_size)
get_filters(category="restaurant", tool="book")
# → {"party_size": {"min": 1, "max": 20}, "date": {...}, "time": {...}}

# Booking params for hair salons (NO party_size!)
get_filters(category="hair_salon", tool="book")
# → {"service": {...}, "date": {...}, "time": {...}, "duration": {...}}
```

**Categories:** `restaurant`, `hair_salon`, `spa`, `fitness`

### `search_venues`

Search for venues by category, city, and filters.

```python
search_venues(
    category="restaurant",
    city="Paris",
    date="2025-01-15",
    party_size=4,
    filters={"cuisine": "French", "price_range": "$$"}
)
```

### `check_availability`

Check available time slots. Parameters vary by category!

```python
# Restaurant (uses party_size)
check_availability(
    venue_id="demo_paris_001",
    category="restaurant",
    params={"date": "2025-01-15", "party_size": 4}
)

# Hair salon (uses service, no party_size)
check_availability(
    venue_id="demo_paris_hair_001",
    category="hair_salon",
    params={"date": "2025-01-15", "service": "Haircut"}
)
```

### `book`

Make a reservation. Parameters vary by category!

```python
# Restaurant booking
book(
    venue_id="demo_paris_001",
    category="restaurant",
    params={"date": "2025-01-15", "time": "19:30", "party_size": 4},
    customer_name="John Doe",
    customer_email="john@example.com",
    customer_phone="+33612345678"
)

# Hair salon booking
book(
    venue_id="demo_paris_hair_001",
    category="hair_salon",
    params={"date": "2025-01-15", "time": "14:00", "service": "Haircut"},
    customer_name="Jane Doe",
    customer_email="jane@example.com",
    customer_phone="+33612345678"
)
```

### `cancel`

Cancel an existing reservation.

```python
cancel(booking_id="booking_abc123")
```

### `find_venue_by_domain`

Find a venue by its website domain.

```python
find_venue_by_domain(domain="venue.example.com")
```

## Architecture

```
dock-ai/
├── src/dock_ai/
│   ├── server.py              # MCP server with 5 tools
│   ├── adapters/
│   │   ├── base.py            # Abstract interface
│   │   └── demo.py            # Demo adapter (mock data)
│   └── registry/
│       ├── database.py        # Supabase client
│       └── registry.py        # Venue → provider mapping
├── supabase/
│   └── migrations/            # Database schema
├── CONTRIBUTING.md            # How to add adapters
└── .env.example               # Environment template
```

## For Booking Platforms

Want to integrate your booking platform with Dock AI?

**Contact us:** [yoann@dockai.co](mailto:yoann@dockai.co)

We'll work with you to:
1. Build an adapter for your API
2. Securely configure credentials
3. Add your venues to the registry

## Adding a New Provider

For developers who want to contribute an adapter, see [CONTRIBUTING.md](CONTRIBUTING.md).

```python
# Example: Adding a new provider
class YourProviderAdapter(BaseAdapter):
    provider_name = "your_provider"

    async def search(self, city, date, party_size, cuisine=None):
        # Call your provider's API
        ...
```

## Contributing

Contributions welcome! See [CONTRIBUTING.md](CONTRIBUTING.md) for details.

## License

MIT
