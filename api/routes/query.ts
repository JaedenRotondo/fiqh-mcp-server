import { Router, Request, Response } from 'express';
import { semanticSearch, getByTopic, getByReference } from '../../src/search/vector-search.js';
import { QueryParamsSchema, MadhabSchema } from '../../src/database/models.js';

const router = Router();

/**
 * POST /api/query
 * Search for fiqh rulings using semantic search
 */
router.post('/query', async (req: Request, res: Response) => {
  try {
    // Validate and parse request body
    const params = QueryParamsSchema.parse(req.body);

    // Perform search
    const results = await semanticSearch(params);

    // Return results
    res.json({
      success: true,
      query: params.query,
      count: results.length,
      results: results.map(r => ({
        entry: r.entry,
        score: r.score,
      })),
    });
  } catch (error) {
    console.error('Query error:', error);

    if (error instanceof Error && error.name === 'ZodError') {
      res.status(400).json({
        success: false,
        error: 'Invalid request parameters',
        details: error.message,
      });
    } else {
      res.status(500).json({
        success: false,
        error: 'Search failed',
        message: error instanceof Error ? error.message : 'Unknown error',
      });
    }
  }
});

/**
 * GET /api/topic/:topic
 * Browse fiqh entries by topic
 */
router.get('/topic/:topic', async (req: Request, res: Response) => {
  try {
    const { topic } = req.params;
    const madhab = req.query.madhab ? MadhabSchema.parse(req.query.madhab) : undefined;
    const limit = req.query.limit ? parseInt(req.query.limit as string, 10) : 20;

    const topicStr = Array.isArray(topic) ? topic[0] : topic;
    const entries = await getByTopic(topicStr, madhab, limit);

    res.json({
      success: true,
      topic,
      madhab,
      count: entries.length,
      entries,
    });
  } catch (error) {
    console.error('Topic browse error:', error);

    res.status(500).json({
      success: false,
      error: 'Failed to browse topic',
      message: error instanceof Error ? error.message : 'Unknown error',
    });
  }
});

/**
 * GET /api/reference
 * Get a specific entry by source reference
 */
router.get('/reference', async (req: Request, res: Response) => {
  try {
    const { source, reference } = req.query;

    if (!source || !reference) {
      res.status(400).json({
        success: false,
        error: 'Missing required parameters: source and reference',
      });
      return;
    }

    const entry = await getByReference(String(source), String(reference));

    if (!entry) {
      res.status(404).json({
        success: false,
        error: 'Entry not found',
      });
      return;
    }

    res.json({
      success: true,
      entry,
    });
  } catch (error) {
    console.error('Reference lookup error:', error);

    res.status(500).json({
      success: false,
      error: 'Failed to lookup reference',
      message: error instanceof Error ? error.message : 'Unknown error',
    });
  }
});

export default router;
