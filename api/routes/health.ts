import { Router, Request, Response } from 'express';
import { getDatabaseStats, getAllTopics, getAllScholars } from '../../src/search/vector-search.js';

const router = Router();

/**
 * GET /health
 * Health check endpoint
 */
router.get('/health', async (req: Request, res: Response) => {
  try {
    const stats = getDatabaseStats();

    res.json({
      status: 'healthy',
      service: 'fiqh-mcp-server',
      version: '1.0.0',
      timestamp: new Date().toISOString(),
      database: {
        totalEntries: stats.totalEntries,
        ready: stats.totalEntries > 0,
      },
    });
  } catch (error) {
    res.status(503).json({
      status: 'unhealthy',
      service: 'fiqh-mcp-server',
      error: error instanceof Error ? error.message : 'Unknown error',
    });
  }
});

/**
 * GET /api/stats
 * Get database statistics
 */
router.get('/stats', async (req: Request, res: Response) => {
  try {
    const stats = getDatabaseStats();
    const topics = getAllTopics();
    const scholars = getAllScholars();

    res.json({
      success: true,
      stats: {
        ...stats,
        topTopics: topics.slice(0, 10),
        topScholars: scholars.slice(0, 10),
      },
    });
  } catch (error) {
    res.status(500).json({
      success: false,
      error: 'Failed to get statistics',
      message: error instanceof Error ? error.message : 'Unknown error',
    });
  }
});

export default router;
