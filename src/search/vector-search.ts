import { ChromaClient } from 'chromadb';
import { appConfig, getChromaUrl } from '../utils/config.js';
import { generateEmbedding } from './embeddings.js';
import { FiqhEntry, SearchResult, QueryParams, Madhab } from '../database/models.js';
import { readFileSync } from 'fs';
import { resolve } from 'path';

/**
 * ChromaDB client instance
 */
let chromaClient: ChromaClient | null = null;

/**
 * Get or create ChromaDB client
 */
function getChromaClient(): ChromaClient {
  if (!chromaClient) {
    chromaClient = new ChromaClient({
      path: getChromaUrl(),
    });
  }
  return chromaClient;
}

/**
 * Load full fiqh database from JSON file
 */
function loadFiqhDatabase(): Map<string, FiqhEntry> {
  try {
    const dataPath = resolve(appConfig.dataPath);
    const data = JSON.parse(readFileSync(dataPath, 'utf-8'));

    const map = new Map<string, FiqhEntry>();
    for (const entry of data) {
      map.set(entry.id, entry as FiqhEntry);
    }

    return map;
  } catch (error) {
    console.error('Error loading fiqh database:', error);
    throw new Error('Failed to load fiqh database. Please ensure data is processed and available.');
  }
}

// Cache the database in memory
const fiqhDatabase = loadFiqhDatabase();

/**
 * Search for fiqh rulings using semantic vector search
 */
export async function semanticSearch(params: QueryParams): Promise<SearchResult[]> {
  try {
    // Generate embedding for query
    const queryEmbedding = await generateEmbedding(params.query);

    // Get ChromaDB client and collection
    const client = getChromaClient();
    // @ts-ignore - ChromaDB types require embeddingFunction but it's optional for pre-computed embeddings
    const collection = await client.getCollection({
      name: appConfig.chromaCollection
    } as any);

    // Build where filter for metadata
    const whereFilter: any = {};

    if (params.madhab) {
      whereFilter.madhab = params.madhab;
    }

    if (params.type) {
      whereFilter.type = params.type;
    }

    // Perform vector search
    const results = await collection.query({
      queryEmbeddings: [queryEmbedding],
      nResults: params.limit || appConfig.defaultSearchLimit,
      where: Object.keys(whereFilter).length > 0 ? whereFilter : undefined,
    });

    // Convert results to SearchResult format
    const searchResults: SearchResult[] = [];

    if (results.ids && results.ids[0]) {
      for (let i = 0; i < results.ids[0].length; i++) {
        const id = results.ids[0][i];
        const distance = results.distances?.[0]?.[i] ?? 0;

        // Calculate similarity score (1 - normalized distance)
        const score = 1 - distance;

        // Skip if below minimum score
        if (score < (params.minScore || appConfig.defaultMinScore)) {
          continue;
        }

        // Get full entry from database
        const entry = fiqhDatabase.get(id);
        if (!entry) {
          console.warn(`Entry not found in database: ${id}`);
          continue;
        }

        // Filter by topics if specified
        if (params.topics && params.topics.length > 0) {
          const hasMatchingTopic = params.topics.some(topic =>
            entry.topics.some(t => t.toLowerCase().includes(topic.toLowerCase()))
          );
          if (!hasMatchingTopic) {
            continue;
          }
        }

        searchResults.push({
          entry,
          score,
          distance,
        });
      }
    }

    return searchResults;
  } catch (error) {
    console.error('Error performing semantic search:', error);
    throw new Error(`Search failed: ${error instanceof Error ? error.message : 'Unknown error'}`);
  }
}

/**
 * Get fiqh entries by topic
 */
export async function getByTopic(topic: string, madhab?: Madhab, limit: number = 20): Promise<FiqhEntry[]> {
  const entries: FiqhEntry[] = [];

  for (const entry of fiqhDatabase.values()) {
    // Check if entry has the topic
    const hasTopicMatch = entry.topics.some(t =>
      t.toLowerCase().includes(topic.toLowerCase()) ||
      topic.toLowerCase().includes(t.toLowerCase())
    );

    if (!hasTopicMatch) {
      continue;
    }

    // Filter by madhab if specified
    if (madhab && entry.madhab && entry.madhab !== madhab) {
      continue;
    }

    entries.push(entry);

    if (entries.length >= limit) {
      break;
    }
  }

  return entries;
}

/**
 * Get a specific fiqh entry by source reference
 */
export async function getByReference(sourceTitle: string, reference: string): Promise<FiqhEntry | null> {
  for (const entry of fiqhDatabase.values()) {
    const titleMatch = entry.source.title.toLowerCase().includes(sourceTitle.toLowerCase());
    const refMatch = entry.source.reference.toLowerCase().includes(reference.toLowerCase());

    if (titleMatch && refMatch) {
      return entry;
    }
  }

  return null;
}

/**
 * Get all unique topics in the database
 */
export function getAllTopics(): { name: string; count: number }[] {
  const topicCounts = new Map<string, number>();

  for (const entry of fiqhDatabase.values()) {
    for (const topic of entry.topics) {
      topicCounts.set(topic, (topicCounts.get(topic) || 0) + 1);
    }
  }

  return Array.from(topicCounts.entries())
    .map(([name, count]) => ({ name, count }))
    .sort((a, b) => b.count - a.count);
}

/**
 * Get all unique scholars in the database
 */
export function getAllScholars(): { name: string; count: number }[] {
  const scholarCounts = new Map<string, number>();

  for (const entry of fiqhDatabase.values()) {
    if (entry.source.scholar) {
      scholarCounts.set(entry.source.scholar, (scholarCounts.get(entry.source.scholar) || 0) + 1);
    }
  }

  return Array.from(scholarCounts.entries())
    .map(([name, count]) => ({ name, count }))
    .sort((a, b) => b.count - a.count);
}

/**
 * Get database statistics
 */
export function getDatabaseStats() {
  const stats = {
    totalEntries: fiqhDatabase.size,
    entriesByType: {} as Record<string, number>,
    entriesByMadhab: {} as Record<string, number>,
    totalTopics: getAllTopics().length,
    totalScholars: getAllScholars().length,
  };

  for (const entry of fiqhDatabase.values()) {
    // Count by type
    stats.entriesByType[entry.type] = (stats.entriesByType[entry.type] || 0) + 1;

    // Count by madhab
    if (entry.madhab) {
      stats.entriesByMadhab[entry.madhab] = (stats.entriesByMadhab[entry.madhab] || 0) + 1;
    }
  }

  return stats;
}
