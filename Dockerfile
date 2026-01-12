FROM node:18-slim

# Install Python for potential data processing
RUN apt-get update && apt-get install -y \
    python3 \
    python3-pip \
    python3-venv \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Copy package files
COPY package*.json ./
COPY tsconfig.json ./

# Install Node dependencies
RUN npm ci

# Copy source code
COPY src ./src
COPY api ./api

# Build TypeScript
RUN npm run build

# Copy scripts (for potential data updates)
COPY scripts ./scripts
COPY requirements.txt ./

# Create data directory structure
RUN mkdir -p data/raw data/processed data/embeddings

# Expose port for REST API
EXPOSE 3000

# Default command runs the REST API server
# Use build/src/index.js for stdio MCP mode
CMD ["node", "build/api/index.js"]
