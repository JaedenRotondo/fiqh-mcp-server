import { Request, Response, NextFunction } from 'express';
import { appConfig } from '../../src/utils/config.js';

/**
 * Authentication middleware for API key validation
 */
export function authenticate(req: Request, res: Response, next: NextFunction): void {
  // Skip auth if no API key is configured (development mode)
  if (!appConfig.apiKey) {
    next();
    return;
  }

  // Get API key from header
  const apiKey = req.headers['x-api-key'] as string;

  if (!apiKey) {
    res.status(401).json({
      error: 'Unauthorized',
      message: 'API key is required. Provide it in the X-API-Key header.',
    });
    return;
  }

  // Validate API key
  if (apiKey !== appConfig.apiKey) {
    res.status(401).json({
      error: 'Unauthorized',
      message: 'Invalid API key.',
    });
    return;
  }

  // API key is valid
  next();
}
