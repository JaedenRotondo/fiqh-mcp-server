# Setting Up Fiqh MCP Server with Claude Code

## Quick Setup

### 1. Find Your Claude Code Config Directory

The config file location depends on your OS:
- **Linux**: `~/.config/claude/claude_desktop_config.json`
- **macOS**: `~/Library/Application Support/Claude/claude_desktop_config.json`
- **Windows**: `%APPDATA%\Claude\claude_desktop_config.json`

### 2. Add MCP Server Configuration

Open (or create) `claude_desktop_config.json` and add this configuration:

```json
{
  "mcpServers": {
    "fiqh-server": {
      "command": "node",
      "args": [
        "/path/to/fiqh-mcp-server/build/index.js"
      ],
      "env": {
        "OPENAI_API_KEY": "your-openai-api-key-here",
        "CHROMA_COLLECTION": "fiqh_embeddings",
        "DATA_PATH": "/path/to/fiqh-mcp-server/data/processed/fiqh_database.json"
      }
    }
  }
}
```

**Note:** Replace the path in `args` with your actual project path if different.

### 3. Restart Claude Code

After saving the config file, restart Claude Code (or Claude Desktop) for changes to take effect.

### 4. Verify Connection

In a new Claude conversation, the MCP server should connect automatically. You'll see the available tools in the tool list.

---

## Available Tools

Once connected, you can use these tools in Claude conversations:

### 1. **query_fiqh** - Semantic Search
Search for Islamic rulings using natural language:
```
"What is the ruling on combining prayers while traveling?"
"Can I pray with shoes on?"
"Is it permissible to fast on Saturdays?"
```

**Parameters:**
- `query` (required): Your question in natural language
- `madhab` (optional): Filter by school - "hanafi", "maliki", "shafi", "hanbali", "general"
- `limit` (optional): Number of results (1-50, default: 5)

### 2. **browse_by_topic** - Topic Browsing
Browse rulings by category:
```
"Show me rulings about prayer"
"Browse fasting topics"
"List all marriage-related fatawa"
```

**Topics available:**
- prayer, fasting, zakat, hajj, purification
- marriage, divorce, family, inheritance
- business, trade, food, manners
- faith, worship, quran, hadith

### 3. **get_ruling_by_reference** - Direct Lookup
Get a specific hadith by reference:
```
"Get Sahih al-Bukhari, Book 1, Hadith 1"
"Show me Sahih Muslim, Book 4, Hadith 2074"
```

### 4. **list_topics** - List All Topics
Get a list of all available topics with entry counts.

### 5. **list_scholars** - List All Scholars
Get a list of all scholars in the database.

### 6. **get_database_stats** - Database Statistics
Get statistics about the fiqh database.

---

## Example Conversation

**You:** What is the Islamic ruling on combining Dhuhr and Asr prayers while traveling?

**Claude:** Let me search the fiqh database for rulings about combining prayers during travel.

*[Claude calls query_fiqh tool with your question]*

**Claude:** Based on the hadith and fatawa, combining prayers (Jam' al-Salat) while traveling is permissible according to authentic sources:

1. **From Sahih Muslim** (Book 4, Hadith 1572):
   Ibn Abbas reported: "The Messenger of Allah combined Dhuhr with Asr and Maghrib with Isha while on a journey..."

2. **Scholarly consensus**: All four madhabs permit combining prayers during travel as a concession (rukhsah).

*[Claude provides detailed answer with proper citations]*

---

## Database Stats

Your fiqh database contains:
- **40,942 hadith** from 9 collections (including all 6 Kutub al-Sittah)
- **4,059 fatawa** from IslamQA
- **Total: 45,001 entries**

Collections include:
- Sahih al-Bukhari (7,277 hadith)
- Sahih Muslim (7,459 hadith)
- Sunan Abi Dawud (5,276 hadith)
- Jami at-Tirmidhi (4,053 hadith)
- Sunan an-Nasa'i (5,768 hadith)
- Sunan Ibn Majah (4,345 hadith)
- Musnad Ahmad (1,374 hadith)
- Sunan ad-Darimi (3,406 hadith)
- Muwatta Malik (1,985 hadith)

---

## Troubleshooting

### MCP Server Not Connecting

1. **Check the path** in `claude_desktop_config.json` is correct
2. **Verify build exists**: `ls /path/to/fiqh-mcp-server/build/index.js`
3. **Check logs**: Claude Code shows MCP connection status in the UI

### No Results Returned

1. **Wait for embeddings**: Ensure the embedding generation completed
2. **Check ChromaDB**: Verify `/path/to/fiqh-mcp-server/data/embeddings/chroma_db` exists
3. **Verify database**: Check that `fiqh_database.json` exists and is not empty

### Slow Queries

- First query might take 2-3 seconds to initialize ChromaDB
- Subsequent queries should be <200ms
- If consistently slow, check your system resources

---

## Manual Testing (Before Claude Code)

You can test the MCP server directly:

```bash
cd /path/to/fiqh-mcp-server
npm start
```

This starts the MCP server in stdio mode. You can send MCP protocol messages to test.

---

## Next Steps

1. ✅ Wait for embedding generation to complete (~30 minutes remaining)
2. ✅ Configure `claude_desktop_config.json` (follow instructions above)
3. ✅ Restart Claude Code
4. ✅ Test with a simple query like "What is wudu?"
5. ✅ Enjoy instant access to 45,000+ Islamic fiqh sources!
