# MCP Usage Guide

This guide explains how to use the Fiqh MCP Server with Claude Code CLI.

## Setup

### 1. Install and Build the Server

```bash
cd /home/jaeden/Projects/personal/fiqh-mcp-server
npm install
npm run build
```

### 2. Configure Claude Code

Add the server to your Claude Code MCP settings file:

**Location**: `~/.config/claude/config.json` (Linux/Mac) or `%APPDATA%\claude\config.json` (Windows)

**Configuration**:
```json
{
  "mcpServers": {
    "fiqh": {
      "command": "node",
      "args": ["/home/jaeden/Projects/personal/fiqh-mcp-server/build/index.js"],
      "env": {
        "OPENAI_API_KEY": "sk-your-api-key-here",
        "CHROMA_HOST": "localhost",
        "CHROMA_PORT": "8000"
      }
    }
  }
}
```

### 3. Start ChromaDB (if running separately)

If you're running ChromaDB as a separate service:

```bash
chroma run --path ./data/embeddings/chroma_db --port 8000
```

Otherwise, the Python scripts will use the persistent client directly.

## Available Tools

The MCP server provides six tools for querying Islamic fiqh:

### 1. query_fiqh

**Purpose**: Semantic search for fiqh rulings using natural language queries

**Parameters**:
- `query` (string, required): Your question or search query
- `madhab` (string, optional): Filter by school of thought: `hanafi`, `maliki`, `shafi`, `hanbali`, or `general`
- `limit` (number, optional): Maximum results to return (1-50, default: 5)

**Examples**:

Basic query:
```
What is the ruling on combining prayers while traveling?
```

With madhab filter:
```
Use query_fiqh to find the Hanafi position on wiping over leather socks
```

Multiple results:
```
Query for 10 results about the conditions of wudu
```

### 2. browse_by_topic

**Purpose**: Browse rulings organized by topic

**Parameters**:
- `topic` (string, required): The topic to browse (e.g., "prayer", "fasting", "zakat")
- `madhab` (string, optional): Filter by school of thought
- `limit` (number, optional): Maximum results (1-100, default: 20)

**Examples**:

```
Browse the topic of prayer

Show me Shafi'i rulings on zakat

List 30 entries about fasting
```

### 3. get_ruling_by_reference

**Purpose**: Retrieve a specific hadith or fatwa by its citation

**Parameters**:
- `source` (string, required): The source name (e.g., "Sahih Bukhari")
- `reference` (string, required): The specific reference (e.g., "Book 2, Hadith 123")

**Examples**:

```
Get the hadith from Sahih Bukhari Book 8 Hadith 432

Find Sahih Muslim Book 4 Hadith 1

Look up IslamQA Fatwa No. 12345
```

### 4. list_topics

**Purpose**: Show all available topics in the database

**Parameters**: None

**Example**:

```
What topics are available in the fiqh database?

List all topics
```

### 5. list_scholars

**Purpose**: Show all scholars whose rulings are in the database

**Parameters**: None

**Example**:

```
Which scholars are included in the database?

List all scholars
```

### 6. get_database_stats

**Purpose**: Get statistics about the fiqh database

**Parameters**: None

**Example**:

```
Show me database statistics

How many entries are in the fiqh database?
```

## Usage Examples

### Example Conversations

**Basic Fiqh Query:**
```
User: What is the ruling on missed Fajr prayer?

Claude: Let me search the fiqh database for you.
[Uses query_fiqh tool with query: "missed Fajr prayer"]

Based on the fiqh database:

### Result 1
**Ruling:** If someone misses Fajr prayer due to oversleeping...
[Full ruling with evidence]
**Source:** Sahih al-Bukhari, Book of Prayer, Hadith 597 [Sahih]
```

**Madhab-Specific Query:**
```
User: What's the Hanafi ruling on the opening supplication in prayer?

Claude: I'll search for the Hanafi position on this.
[Uses query_fiqh with madhab filter: "hanafi"]

Found 3 Hanafi rulings on the opening supplication:
[Results with Hanafi-specific rulings]
```

**Topic Browsing:**
```
User: Show me some rulings about Ramadan fasting

Claude: Let me browse the fasting topic for you.
[Uses browse_by_topic with topic: "fasting"]

Found 15 entries related to fasting:
[List of rulings organized by relevance]
```

**Reference Lookup:**
```
User: What does Sahih Bukhari Book 2 Hadith 123 say?

Claude: I'll look up that specific hadith.
[Uses get_ruling_by_reference]

Here's the hadith you requested:
[Full hadith text with translation and metadata]
```

## Tips for Effective Usage

### 1. Be Specific in Queries

**Good**: "What are the conditions for prayer to be valid?"
**Better**: "What are the conditions of validity for salah in the Hanafi madhab?"

### 2. Use Madhab Filters When Needed

If you're following a specific school:
```
Always show me Maliki rulings about purification
```

### 3. Explore Topics First

Before asking specific questions, browse topics to see what's available:
```
List all topics in the database
Then browse the topic that interests you
```

### 4. Compare Madhabs

Ask comparative questions:
```
What's the Hanafi ruling on wiping over socks?
[Then] What's the Shafi'i ruling on the same issue?
```

### 5. Request Varying Detail Levels

- For quick answers: "Brief ruling on..."
- For detailed answers: "Explain in detail the ruling on..."
- For evidence: "Show me the evidence for..."

## Understanding Results

### Result Format

Each result includes:

1. **Question** (for fatawa): The original question asked
2. **Ruling**: The actual fiqh content
3. **Evidence**: Supporting Quran verses and hadith
4. **Metadata**:
   - Madhab (school of thought)
   - Topics (categories)
   - Type (hadith, fatwa, or classical text)
5. **Source**: Citation with:
   - Title (e.g., "Sahih al-Bukhari")
   - Reference (e.g., "Book 2, Hadith 123")
   - Authenticity grade (for hadith): Sahih, Hasan, Daif
   - URL (when available)

### Authenticity Grades

- **✓ Sahih**: Authentic - highest level of authenticity
- **~ Hasan**: Good - acceptable but not as strong as Sahih
- **✗ Daif**: Weak - some weakness in the chain of narration
- **✗✗ Mawdu**: Fabricated - not authentic

## Troubleshooting

### Server Not Responding

1. Check if the server is built:
   ```bash
   npm run build
   ```

2. Verify the path in your config file is correct

3. Check environment variables in the MCP config

### No Results Found

1. Try broader search terms
2. Check if data has been collected and processed
3. Verify ChromaDB is running and has embeddings

### ChromaDB Connection Error

1. Ensure ChromaDB port (8000) is correct in config
2. If using persistent client, check the data path
3. Verify embeddings were generated successfully

### OpenAI API Errors

1. Check your API key is valid
2. Verify you have credits remaining
3. Check network connectivity

## Advanced Usage

### Batch Queries

Ask multiple related questions:
```
I have questions about wudu:
1. What breaks wudu?
2. Can I wipe over regular socks?
3. Do I need wudu for Quran recitation?

Please answer each one using the fiqh database.
```

### Comparative Analysis

```
Compare the four madhabs' rulings on raising hands during prayer
```

### Research Mode

```
I'm researching the topic of zakat on gold. Please:
1. Browse the zakat topic
2. Find specific rulings on gold
3. Show me the evidence from hadith
4. Summarize the differences between madhabs if any
```

## Best Practices

1. **Always cite sources** when sharing rulings
2. **Consult qualified scholars** for personal situations
3. **Cross-reference** important rulings with traditional texts
4. **Understand context** - some rulings are situation-specific
5. **Respect differences** between madhabs - all are valid schools of thought

## Support

If you encounter issues:
1. Check the main README.md
2. Review error messages in Claude Code console
3. Open an issue on GitHub with details
