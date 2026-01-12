# REST API Documentation

The Fiqh MCP Server provides a REST API for integration with GitHub Actions, web applications, and other services.

## Base URL

```
http://localhost:3000
```

## Authentication

Most endpoints require an API key passed in the `X-API-Key` header:

```bash
curl -H "X-API-Key: your-api-key" http://localhost:3000/api/query
```

Configure your API key in the `.env` file:
```
FIQH_API_KEY=your-secret-api-key-here
```

## Rate Limiting

- **Standard endpoints**: 100 requests per hour per IP
- Rate limit information is returned in headers:
  - `RateLimit-Limit`: Maximum requests allowed
  - `RateLimit-Remaining`: Requests remaining
  - `RateLimit-Reset`: Time when limit resets

## Endpoints

### Health Check

#### GET /health

Check if the server is running and database is loaded.

**Authentication**: None required

**Response**:
```json
{
  "status": "healthy",
  "service": "fiqh-mcp-server",
  "version": "1.0.0",
  "timestamp": "2024-01-15T10:30:00.000Z",
  "database": {
    "totalEntries": 5000,
    "ready": true
  }
}
```

### Database Statistics

#### GET /api/stats

Get statistics about the fiqh database.

**Authentication**: Required

**Response**:
```json
{
  "success": true,
  "stats": {
    "totalEntries": 5000,
    "entriesByType": {
      "hadith": 4500,
      "fatwa": 500
    },
    "entriesByMadhab": {
      "hanafi": 150,
      "maliki": 120,
      "shafi": 130,
      "hanbali": 100
    },
    "totalTopics": 45,
    "totalScholars": 12,
    "topTopics": [
      {"name": "prayer", "count": 850},
      {"name": "purification", "count": 620}
    ],
    "topScholars": [
      {"name": "IslamQA Scholars", "count": 500}
    ]
  }
}
```

### Query Fiqh Rulings

#### POST /api/query

Search for fiqh rulings using semantic search.

**Authentication**: Required

**Request Body**:
```json
{
  "query": "What is the ruling on missed prayers?",
  "madhab": "hanafi",
  "limit": 5,
  "minScore": 0.5
}
```

**Parameters**:
- `query` (string, required): Search query
- `madhab` (string, optional): Filter by madhab: `hanafi`, `maliki`, `shafi`, `hanbali`, `general`
- `limit` (number, optional): Max results (1-50, default: 5)
- `minScore` (number, optional): Minimum similarity score (0-1, default: 0.5)

**Response**:
```json
{
  "success": true,
  "query": "What is the ruling on missed prayers?",
  "count": 3,
  "results": [
    {
      "entry": {
        "id": "bukhari_597",
        "type": "hadith",
        "ruling": "The Prophet said: 'Whoever forgets a prayer...'",
        "evidence": ["Quran 4:103"],
        "source": {
          "title": "Sahih al-Bukhari",
          "reference": "Book 8, Hadith 597",
          "url": "https://sunnah.com/bukhari/8/597"
        },
        "authenticity": "sahih",
        "topics": ["prayer", "missed-prayers"]
      },
      "score": 0.89
    }
  ]
}
```

**Error Response**:
```json
{
  "success": false,
  "error": "Invalid request parameters",
  "details": "query is required"
}
```

### Browse by Topic

#### GET /api/topic/:topic

Browse fiqh entries by topic.

**Authentication**: Required

**URL Parameters**:
- `topic` (string, required): Topic name (e.g., "prayer", "fasting")

**Query Parameters**:
- `madhab` (string, optional): Filter by madhab
- `limit` (number, optional): Max results (1-100, default: 20)

**Example**:
```bash
GET /api/topic/prayer?madhab=hanafi&limit=10
```

**Response**:
```json
{
  "success": true,
  "topic": "prayer",
  "madhab": "hanafi",
  "count": 10,
  "entries": [
    {
      "id": "bukhari_500",
      "type": "hadith",
      "ruling": "...",
      "source": {...},
      "topics": ["prayer"],
      "madhab": "hanafi"
    }
  ]
}
```

### Get by Reference

#### GET /api/reference

Retrieve a specific entry by source reference.

**Authentication**: Required

**Query Parameters**:
- `source` (string, required): Source title (e.g., "Sahih Bukhari")
- `reference` (string, required): Specific reference (e.g., "Book 2, Hadith 123")

**Example**:
```bash
GET /api/reference?source=Sahih Bukhari&reference=Book 2, Hadith 123
```

**Response**:
```json
{
  "success": true,
  "entry": {
    "id": "bukhari_123",
    "type": "hadith",
    "ruling": "...",
    "source": {
      "title": "Sahih al-Bukhari",
      "reference": "Book 2, Hadith 123"
    }
  }
}
```

**Not Found Response**:
```json
{
  "success": false,
  "error": "Entry not found"
}
```

## Error Codes

| Code | Meaning |
|------|---------|
| 200 | Success |
| 400 | Bad Request - Invalid parameters |
| 401 | Unauthorized - Missing or invalid API key |
| 404 | Not Found - Resource doesn't exist |
| 429 | Too Many Requests - Rate limit exceeded |
| 500 | Internal Server Error - Server error |
| 503 | Service Unavailable - Database not ready |

## GitHub Actions Integration

### Example Workflow

Create `.github/workflows/fiqh-query.yml`:

```yaml
name: Query Fiqh Database

on:
  workflow_dispatch:
    inputs:
      query:
        description: 'Fiqh query'
        required: true
        type: string
      madhab:
        description: 'Madhab filter'
        required: false
        type: choice
        options:
          - ''
          - hanafi
          - maliki
          - shafi
          - hanbali

jobs:
  query:
    runs-on: ubuntu-latest
    steps:
      - name: Query Fiqh API
        run: |
          response=$(curl -s -X POST https://your-api-url.com/api/query \
            -H "Content-Type: application/json" \
            -H "X-API-Key: ${{ secrets.FIQH_API_KEY }}" \
            -d "{\"query\": \"${{ github.event.inputs.query }}\", \"madhab\": \"${{ github.event.inputs.madhab }}\"}")

          echo "Response: $response"

          # Parse and display results
          echo "$response" | jq '.results[] | .entry.ruling' -r

      - name: Create Issue with Results
        if: success()
        uses: actions/github-script@v6
        with:
          script: |
            // Create an issue with the query results
            github.rest.issues.create({
              owner: context.repo.owner,
              repo: context.repo.repo,
              title: 'Fiqh Query: ${{ github.event.inputs.query }}',
              body: 'Query results will be posted here...'
            });
```

### Secrets Setup

Add your API key to GitHub Secrets:
1. Go to repository Settings → Secrets → Actions
2. Click "New repository secret"
3. Name: `FIQH_API_KEY`
4. Value: Your API key
5. Click "Add secret"

## Client Examples

### cURL

```bash
# Basic query
curl -X POST http://localhost:3000/api/query \
  -H "Content-Type: application/json" \
  -H "X-API-Key: your-api-key" \
  -d '{"query": "wudu conditions", "limit": 3}'

# Topic browse
curl -X GET "http://localhost:3000/api/topic/prayer?limit=5" \
  -H "X-API-Key: your-api-key"

# Health check
curl http://localhost:3000/health
```

### JavaScript/TypeScript

```typescript
const API_BASE = 'http://localhost:3000';
const API_KEY = 'your-api-key';

async function queryFiqh(query: string, madhab?: string) {
  const response = await fetch(`${API_BASE}/api/query`, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
      'X-API-Key': API_KEY,
    },
    body: JSON.stringify({ query, madhab, limit: 5 }),
  });

  const data = await response.json();
  return data;
}

// Usage
const results = await queryFiqh('prayer times', 'hanafi');
console.log(results.results);
```

### Python

```python
import requests

API_BASE = 'http://localhost:3000'
API_KEY = 'your-api-key'

def query_fiqh(query, madhab=None, limit=5):
    response = requests.post(
        f'{API_BASE}/api/query',
        headers={
            'Content-Type': 'application/json',
            'X-API-Key': API_KEY
        },
        json={
            'query': query,
            'madhab': madhab,
            'limit': limit
        }
    )
    return response.json()

# Usage
results = query_fiqh('What breaks wudu?', madhab='shafi')
for result in results['results']:
    print(result['entry']['ruling'])
```

## Deployment

### Local Development

```bash
npm run api
# Server runs on http://localhost:3000
```

### Production Deployment

Consider using:
- **Docker**: Container for easy deployment
- **PM2**: Process manager for Node.js
- **Nginx**: Reverse proxy with SSL
- **Cloud Services**: Deploy to AWS, GCP, or Azure

Example PM2 config (`ecosystem.config.js`):
```javascript
module.exports = {
  apps: [{
    name: 'fiqh-api',
    script: './build/api/index.js',
    instances: 2,
    exec_mode: 'cluster',
    env: {
      NODE_ENV: 'production',
      API_PORT: 3000
    }
  }]
};
```

## Best Practices

1. **Always use HTTPS** in production
2. **Rotate API keys** regularly
3. **Monitor rate limits** to avoid blocking legitimate users
4. **Cache responses** when appropriate
5. **Implement logging** for debugging and monitoring
6. **Use environment variables** for sensitive configuration
7. **Set up CORS** properly for web applications

## Support

For API issues or questions:
- Check server logs for errors
- Verify API key is correct
- Ensure database is loaded (check `/health`)
- Review rate limit headers
- Open an issue on GitHub
