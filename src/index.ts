#!/usr/bin/env node

/**
 * Fiqh MCP Server
 * Entry point for the Islamic Fiqh Model Context Protocol server
 */

import { runServer } from './server.js';

// Handle uncaught errors
process.on('uncaughtException', (error) => {
  console.error('Uncaught exception:', error);
  process.exit(1);
});

process.on('unhandledRejection', (reason, promise) => {
  console.error('Unhandled rejection at:', promise, 'reason:', reason);
  process.exit(1);
});

// Run the server
runServer().catch((error) => {
  console.error('Failed to start server:', error);
  process.exit(1);
});
