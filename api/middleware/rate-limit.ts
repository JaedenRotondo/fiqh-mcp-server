import rateLimit from 'express-rate-limit';

/**
 * Rate limiter for API endpoints
 * Limits: 100 requests per hour per IP
 */
export const apiRateLimiter = rateLimit({
  windowMs: 60 * 60 * 1000, // 1 hour
  max: 100, // 100 requests per hour
  message: {
    error: 'Too Many Requests',
    message: 'You have exceeded the 100 requests per hour limit. Please try again later.',
  },
  standardHeaders: true, // Return rate limit info in the `RateLimit-*` headers
  legacyHeaders: false, // Disable the `X-RateLimit-*` headers
});

/**
 * Stricter rate limiter for expensive operations
 * Limits: 20 requests per hour per IP
 */
export const strictRateLimiter = rateLimit({
  windowMs: 60 * 60 * 1000, // 1 hour
  max: 20, // 20 requests per hour
  message: {
    error: 'Too Many Requests',
    message: 'You have exceeded the 20 requests per hour limit for this endpoint. Please try again later.',
  },
  standardHeaders: true,
  legacyHeaders: false,
});
