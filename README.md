# Fiqh MCP Server

A Model Context Protocol (MCP) server that provides access to Islamic fiqh (jurisprudence) rulings from classical texts and all four Sunni madhabs (Hanafi, Maliki, Shafi'i, Hanbali). The system uses AI-powered semantic search to find relevant rulings and returns answers with proper source citations.

## Features

- **Semantic Search**: AI-powered search using OpenAI embeddings and vector similarity
- **Comprehensive Coverage**: Hadith from the six authentic books (Kutub al-Sittah) and contemporary fatawa
- **Madhab Filtering**: Filter rulings by specific schools of Islamic jurisprudence
- **Source Citations**: All rulings include proper source attribution and references
- **MCP Integration**: Works seamlessly with Claude Code CLI
- **REST API**: HTTP endpoints for GitHub Actions and other integrations
- **Topic Browsing**: Browse rulings by categories like prayer, fasting, zakat, etc.

## Quick Start

### Prerequisites

- Node.js 18+ and npm
- Python 3.10+
- OpenAI API key

### Installation

1. **Clone the repository**
   ```bash
   cd /home/jaeden/Projects/personal/fiqh-mcp-server
   ```

2. **Install Node.js dependencies**
   ```bash
   npm install
   ```

3. **Set up Python environment**
   ```bash
   python3 -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   pip install -r requirements.txt
   ```

4. **Configure environment variables**
   ```bash
   cp .env.example .env
   # Edit .env and add your OPENAI_API_KEY
   ```

5. **Collect and process data**
   ```bash
   # Scrape hadith from sunnah.com
   python scripts/scrape_sunnah_com.py

   # Scrape fatawa (optional)
   python scripts/scrape_islamqa.py

   # Process and clean the data
   python scripts/process_texts.py

   # Generate embeddings
   python scripts/generate_embeddings.py
   ```

6. **Build the TypeScript code**
   ```bash
   npm run build
   ```

### Usage

#### As MCP Server (with Claude Code)

Add to your Claude Code MCP settings (usually `~/.config/claude/config.json`):

```json
{
  "mcpServers": {
    "fiqh": {
      "command": "node",
      "args": ["/home/jaeden/Projects/personal/fiqh-mcp-server/build/index.js"],
      "env": {
        "OPENAI_API_KEY": "your-key-here"
      }
    }
  }
}
```

Then use in Claude Code:
```
Ask Claude: "Use the query_fiqh tool to find the Hanafi ruling on combining prayers"
```

#### As REST API Server

Start the API server:
```bash
npm run api
```

Make requests:
```bash
curl -X POST http://localhost:3000/api/query \
  -H "Content-Type: application/json" \
  -H "X-API-Key: your-api-key" \
  -d '{"query": "What is the ruling on missed prayers?", "limit": 3}'
```

## Available Tools

### MCP Tools

1. **query_fiqh** - Semantic search for fiqh rulings
   - Parameters: `query` (required), `madhab` (optional), `limit` (optional)
   - Example: `{"query": "What is the ruling on wiping over socks?", "madhab": "hanafi"}`

2. **browse_by_topic** - Browse rulings by topic
   - Parameters: `topic` (required), `madhab` (optional), `limit` (optional)
   - Example: `{"topic": "prayer", "madhab": "shafi"}`

3. **get_ruling_by_reference** - Get specific hadith/fatwa by reference
   - Parameters: `source` (required), `reference` (required)
   - Example: `{"source": "Sahih Bukhari", "reference": "Book 2, Hadith 123"}`

4. **list_topics** - List all available topics
5. **list_scholars** - List all scholars in the database
6. **get_database_stats** - Get database statistics

### API Endpoints

- `GET /health` - Health check
- `GET /api/stats` - Database statistics
- `POST /api/query` - Search for rulings
- `GET /api/topic/:topic` - Browse by topic
- `GET /api/reference` - Get by reference

## Data Sources

The server collects data from:

- **Sunnah.com API**: Authenticated hadith from the six books (Bukhari, Muslim, Abu Dawud, Tirmidhi, Nasai, Ibn Majah)
- **IslamQA.info**: Contemporary fatawa with madhab classifications
- More sources can be added via additional scraping scripts

See [docs/DATA_SOURCES.md](docs/DATA_SOURCES.md) for detailed information.

## Documentation

- [MCP Usage Guide](docs/MCP_USAGE.md) - How to use with Claude Code
- [API Documentation](docs/API.md) - REST API reference
- [Data Sources](docs/DATA_SOURCES.md) - Information about data sources

## Development

```bash
# Run in development mode with hot reload
npm run dev

# Run API server in development mode
npm run api

# Build TypeScript
npm run build

# Run tests
npm test

# Lint code
npm run lint
```

## Architecture

```
┌─────────────────┐
│   Claude Code   │
│   MCP Client    │
└────────┬────────┘
         │ stdio
         ▼
┌─────────────────┐     ┌──────────────┐
│   MCP Server    │────▶│   ChromaDB   │
│  (TypeScript)   │     │ Vector Store │
└────────┬────────┘     └──────────────┘
         │
         ├─────▶ OpenAI Embeddings API
         │
         └─────▶ Fiqh Database (JSON)

┌─────────────────┐
│  REST API       │
│  (Express.js)   │
└─────────────────┘
         ▲
         │ HTTP
         │
┌─────────────────┐
│ GitHub Actions  │
│ External Apps   │
└─────────────────┘
```

## Disclaimer

This is a research and educational tool. Users should:

- Consult qualified scholars for personal religious rulings
- Verify information from authoritative sources
- Understand that AI-powered search may not always return perfectly relevant results
- Use this as a supplementary research tool, not as a replacement for traditional Islamic scholarship

## License

MIT License - See LICENSE file for details

## Contributing

Contributions are welcome! Please:

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Submit a pull request

## Support

For issues or questions:
- Open an issue on GitHub
- Check the documentation in the `docs/` folder

## Acknowledgments

- Data sourced from Sunnah.com and IslamQA.info
- Built using the Model Context Protocol by Anthropic
- Powered by OpenAI embeddings
