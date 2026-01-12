#!/usr/bin/env node

/**
 * REST API Server for Fiqh MCP
 * Provides HTTP endpoints for GitHub Actions and public access
 */

import express, { Express, Request, Response, NextFunction } from 'express';
import cors from 'cors';
import { appConfig } from '../src/utils/config.js';
import { authenticate } from './middleware/auth.js';
import { apiRateLimiter } from './middleware/rate-limit.js';
import queryRoutes from './routes/query.js';
import healthRoutes from './routes/health.js';

/**
 * Create and configure Express app
 */
function createApp(): Express {
  const app = express();

  // Middleware
  app.use(cors());
  app.use(express.json());

  // Logging middleware
  app.use((req: Request, res: Response, next: NextFunction) => {
    console.log(`${new Date().toISOString()} ${req.method} ${req.path}`);
    next();
  });

  // Public routes (no auth required)
  app.use('/', healthRoutes);

  // Apply rate limiting and authentication to API routes
  app.use('/api', apiRateLimiter);
  app.use('/api', authenticate);
  app.use('/api', queryRoutes);

  // Root endpoint
  app.get('/', (req: Request, res: Response) => {
    res.json({
      service: 'Fiqh MCP Server API',
      version: '1.0.0',
      documentation: '/docs',
      endpoints: {
        health: 'GET /health',
        stats: 'GET /api/stats',
        query: 'POST /api/query',
        topic: 'GET /api/topic/:topic',
        reference: 'GET /api/reference',
      },
    });
  });

  // 404 handler
  app.use((req: Request, res: Response) => {
    res.status(404).json({
      error: 'Not Found',
      message: `Route ${req.method} ${req.path} not found`,
    });
  });

  // Error handler
  app.use((err: Error, req: Request, res: Response, next: NextFunction) => {
    console.error('Unhandled error:', err);
    res.status(500).json({
      error: 'Internal Server Error',
      message: err.message,
    });
  });

  return app;
}

/**
 * Start the API server
 */
function startServer(): void {
  const app = createApp();
  const port = appConfig.apiPort;

  app.listen(port, () => {
    console.log(`\n${'='.repeat(60)}`);
    console.log('Fiqh MCP API Server');
    console.log(`${'='.repeat(60)}`);
    console.log(`Server running on: http://localhost:${port}`);
    console.log(`Health check: http://localhost:${port}/health`);
    console.log(`API docs: http://localhost:${port}/docs`);
    console.log(`\nAuthentication: ${appConfig.apiKey ? 'Enabled (API key required)' : 'Disabled (development mode)'}`);
    console.log(`Rate limiting: 100 requests/hour per IP`);
    console.log(`${'='.repeat(60)}\n`);
  });
}

// Start the server
startServer();
