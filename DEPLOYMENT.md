# Deployment Guide - Fiqh MCP Server

## Production Deployment with Docker

### Prerequisites

- Docker and Docker Compose installed
- OpenAI API key
- Pre-generated embeddings and database files

### Setup Instructions

#### 1. Clone the Repository

```bash
cd ~/
git clone https://github.com/JaedenRotondo/fiqh-mcp-server.git
cd fiqh-mcp-server
```

#### 2. Configure Environment Variables

Create a `.env` file:

```bash
cp .env.example .env
nano .env
```

Add your configuration:

```env
OPENAI_API_KEY=your-openai-api-key-here
API_KEY=your-secure-api-key-for-rest-api
CHROMA_COLLECTION=fiqh_embeddings
EMBEDDING_MODEL=text-embedding-3-small
PORT=3000
```

#### 3. Copy Data Files

The data directory should contain:
- `data/processed/fiqh_database.json` - The processed fiqh database
- `data/embeddings/chroma_db/` - The ChromaDB embeddings

**Option A: Copy from existing machine**

```bash
# On the source machine (where data exists)
cd /path/to/fiqh-mcp-server
tar -czf fiqh-data.tar.gz data/

# Transfer to production server
scp fiqh-data.tar.gz user@production-server:~/fiqh-mcp-server/

# On production server
cd ~/fiqh-mcp-server
tar -xzf fiqh-data.tar.gz
rm fiqh-data.tar.gz
```

**Option B: Generate data on production server**

```bash
# Set up Python environment
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt

# Scrape and process data
python scripts/scrape_sunnah_com.py
python scripts/scrape_islamqa.py
python scripts/process_texts.py
python scripts/generate_embeddings.py
```

#### 4. Build and Start the Docker Container

```bash
# Build the image
docker-compose build

# Start the service
docker-compose up -d

# Check logs
docker-compose logs -f
```

#### 5. Verify Deployment

Check the container is running:

```bash
docker ps | grep fiqh-mcp-server
```

Test the REST API:

```bash
curl http://localhost:3001/health
```

Test a query:

```bash
curl -X POST http://localhost:3001/api/query \
  -H "Content-Type: application/json" \
  -H "X-API-Key: your-api-key" \
  -d '{"query": "What is wudu?", "limit": 3}'
```

### Service Management

#### Start/Stop/Restart

```bash
# Start
docker-compose up -d

# Stop
docker-compose down

# Restart
docker-compose restart

# View logs
docker-compose logs -f

# Update and restart
git pull
docker-compose build
docker-compose up -d
```

#### Check Status

```bash
# Container status
docker-compose ps

# Resource usage
docker stats fiqh-mcp-server

# Logs
docker-compose logs --tail 100
```

### Accessing the Service

#### REST API

The REST API is accessible at:
- Local: `http://localhost:3001`
- Network: `http://<server-ip>:3001`

#### MCP Server (stdio mode)

To use with Claude Code from the same machine:

1. Update your Claude Code config (`~/.config/claude/claude_desktop_config.json`):

```json
{
  "mcpServers": {
    "fiqh": {
      "command": "docker",
      "args": [
        "exec",
        "-i",
        "fiqh-mcp-server",
        "node",
        "build/index.js"
      ]
    }
  }
}
```

2. Restart Claude Code

### Monitoring

#### Add to Monit (if available)

Create `/etc/monit/conf-enabled/fiqh-mcp`:

```
check process fiqh-mcp-server matching "fiqh-mcp-server"
  start program = "/usr/bin/docker start fiqh-mcp-server"
  stop program = "/usr/bin/docker stop fiqh-mcp-server"
  if does not exist for 3 cycles then restart
  if failed host localhost port 3001 protocol http
    request /health
    with timeout 10 seconds
    for 2 cycles
  then restart
```

Reload monit:

```bash
sudo monit reload
sudo monit status
```

### Backup

#### Backup Data Directory

```bash
# Create backup
docker-compose down
tar -czf fiqh-backup-$(date +%Y%m%d).tar.gz data/
docker-compose up -d

# Restore from backup
docker-compose down
tar -xzf fiqh-backup-YYYYMMDD.tar.gz
docker-compose up -d
```

### Updating

#### Update Code

```bash
cd ~/fiqh-mcp-server
git pull
docker-compose build
docker-compose up -d
```

#### Update Data

If you need to refresh the hadith database:

```bash
docker-compose down

# Run data update scripts
source venv/bin/activate
python scripts/scrape_sunnah_com.py
python scripts/process_texts.py
python scripts/generate_embeddings.py

docker-compose up -d
```

### Troubleshooting

#### Container won't start

```bash
# Check logs
docker-compose logs

# Check Docker status
sudo systemctl status docker

# Rebuild from scratch
docker-compose down
docker-compose build --no-cache
docker-compose up -d
```

#### API not responding

```bash
# Check if port is accessible
curl http://localhost:3001/health

# Check container networking
docker network inspect fiqh-mcp-server_fiqh-network

# Check if service is listening
docker exec fiqh-mcp-server netstat -tulpn | grep 3000
```

#### Missing embeddings

```bash
# Check data directory
ls -la data/embeddings/chroma_db/

# If missing, you need to copy or regenerate embeddings
# See Step 3 above
```

### Security Notes

1. **API Key**: Change the default API_KEY in `.env`
2. **Firewall**: Consider limiting access to port 3001
3. **Secrets**: Never commit `.env` file to git
4. **Updates**: Keep Docker and base images updated

### Ports

- **3001**: REST API (exposed to host)
- **3000**: Internal container port

To change the external port, edit `docker-compose.yml`:

```yaml
ports:
  - "YOUR_PORT:3000"
```

### Resource Requirements

- **Memory**: ~500MB (with embeddings loaded)
- **Disk**:
  - Code: ~50MB
  - Data: ~500MB (embeddings + database)
  - Total: ~1GB recommended
- **CPU**: Minimal (queries are mostly I/O bound)

### Support

For issues:
1. Check logs: `docker-compose logs -f`
2. Verify data files exist and are accessible
3. Ensure OpenAI API key is valid
4. Check GitHub issues: https://github.com/JaedenRotondo/fiqh-mcp-server/issues
