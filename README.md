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
│  ├── search_venues           - Search venues by city           │
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

### `search_venues`

Search for venues by city, date, and party size.

```python
search_venues(
    city="Paris",
    date="2025-01-15",
    party_size=4,
    cuisine="French"  # optional
)
```

### `check_availability`

Check available time slots for a specific venue.

```python
check_availability(
    venue_id="demo_paris_001",
    date="2025-01-15",
    party_size=4
)
```

### `book`

Make a reservation.

```python
book(
    venue_id="demo_paris_001",
    date="2025-01-15",
    time="19:30",
    party_size=4,
    customer_name="John Doe",
    customer_email="john@example.com",
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

## Adding a New Provider

Want to add support for a new booking platform? See [CONTRIBUTING.md](CONTRIBUTING.md) for a step-by-step guide.

```python
# Example: Adding a new provider
class YourProviderAdapter(BaseAdapter):
    provider_name = "your_provider"

    async def search(self, city, date, party_size, cuisine=None):
        # Call your provider's API
        ...
```

## Contributing

Contributions are welcome! The most impactful contribution is adding new booking provider adapters. See [CONTRIBUTING.md](CONTRIBUTING.md) for details.

## License

MIT
