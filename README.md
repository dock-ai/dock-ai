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
│  ├── search_restaurants      - Search restaurants by city      │
│  ├── check_availability      - Check available time slots      │
│  ├── book_table              - Make a reservation              │
│  ├── cancel_booking          - Cancel a reservation            │
│  └── find_restaurant_by_domain - Find by website               │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
                              │
        ┌─────────────────────┼─────────────────────┐
        ▼                     ▼                     ▼
   ┌─────────┐           ┌─────────┐           ┌─────────┐
   │ Zenchef │           │ Planity │           │ TheFork │
   └─────────┘           └─────────┘           └─────────┘
```

## Quick Start

### 1. Clone and Install

```bash
git clone https://github.com/yoannarz/dock-ai.git
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
      "args": ["-m", "booking_hub.server"],
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

> "Search for French restaurants in Paris for 4 people on January 15th"

## Available Tools

### `search_restaurants`

Search for restaurants by city, date, and party size.

```python
search_restaurants(
    city="Paris",
    date="2025-01-15",
    party_size=4,
    cuisine="French"  # optional
)
```

### `check_availability`

Check available time slots for a specific restaurant.

```python
check_availability(
    restaurant_id="rest_paris_001",
    date="2025-01-15",
    party_size=4
)
```

### `book_table`

Make a reservation.

```python
book_table(
    restaurant_id="rest_paris_001",
    date="2025-01-15",
    time="19:30",
    party_size=4,
    customer_name="John Doe",
    customer_email="john@example.com",
    customer_phone="+33612345678"
)
```

### `cancel_booking`

Cancel an existing reservation.

```python
cancel_booking(booking_id="booking_abc123")
```

### `find_restaurant_by_domain`

Find a restaurant by its website domain.

```python
find_restaurant_by_domain(domain="lepetitparis.fr")
```

## Architecture

```
dock-ai/
├── src/booking_hub/
│   ├── server.py              # MCP server with 5 tools
│   ├── adapters/
│   │   ├── base.py            # Abstract interface
│   │   └── zenchef.py         # Zenchef adapter (mock)
│   └── registry/
│       ├── database.py        # Supabase client
│       └── registry.py        # Restaurant → provider mapping
├── supabase/
│   └── migrations/            # Database schema
├── CONTRIBUTING.md            # How to add adapters
└── .env.example               # Environment template
```

## Adding a New Provider

Want to add support for a new booking platform? See [CONTRIBUTING.md](CONTRIBUTING.md) for a step-by-step guide.

```python
# Example: Adding Planity support
class PlanityAdapter(BaseAdapter):
    provider_name = "planity"

    async def search(self, city, date, party_size, cuisine=None):
        # Call Planity API
        ...
```

## Supported Platforms

| Platform | Status | Notes |
|----------|--------|-------|
| Zenchef | Mock | Ready for production integration |
| Planity | Planned | Looking for API partnership |
| TheFork | Planned | Looking for API partnership |
| OpenTable | Planned | Looking for API partnership |
| Resy | Planned | Looking for API partnership |

## Contributing

Contributions are welcome! The most impactful contribution is adding new booking provider adapters. See [CONTRIBUTING.md](CONTRIBUTING.md) for details.

## License

MIT
