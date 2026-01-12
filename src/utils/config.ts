import { config } from 'dotenv';
import { z } from 'zod';

// Load environment variables
config();

/**
 * Configuration schema with validation
 */
const ConfigSchema = z.object({
  // OpenAI Configuration
  openaiApiKey: z.string().min(1, 'OPENAI_API_KEY is required'),
  embeddingModel: z.string().default('text-embedding-3-small'),

  // ChromaDB Configuration
  chromaHost: z.string().default('localhost'),
  chromaPort: z.number().default(8000),
  chromaCollection: z.string().default('fiqh_embeddings'),

  // API Configuration
  apiPort: z.number().default(3000),
  apiKey: z.string().optional(),

  // Data Configuration
  dataPath: z.string().default('./data/processed/fiqh_database.json'),
  rawDataPath: z.string().default('./data/raw'),

  // Search Configuration
  defaultSearchLimit: z.number().default(5),
  defaultMinScore: z.number().default(0.5),
  maxSearchLimit: z.number().default(50),

  // Environment
  nodeEnv: z.enum(['development', 'production', 'test']).default('development'),
});

/**
 * Parse and validate configuration from environment variables
 */
function loadConfig() {
  try {
    const rawConfig = {
      // OpenAI
      openaiApiKey: process.env.OPENAI_API_KEY || '',
      embeddingModel: process.env.EMBEDDING_MODEL || 'text-embedding-3-small',

      // ChromaDB
      chromaHost: process.env.CHROMA_HOST || 'localhost',
      chromaPort: parseInt(process.env.CHROMA_PORT || '8000', 10),
      chromaCollection: process.env.CHROMA_COLLECTION || 'fiqh_embeddings',

      // API
      apiPort: parseInt(process.env.API_PORT || '3000', 10),
      apiKey: process.env.FIQH_API_KEY,

      // Data
      dataPath: process.env.DATA_PATH || './data/processed/fiqh_database.json',
      rawDataPath: process.env.RAW_DATA_PATH || './data/raw',

      // Search
      defaultSearchLimit: parseInt(process.env.DEFAULT_SEARCH_LIMIT || '5', 10),
      defaultMinScore: parseFloat(process.env.DEFAULT_MIN_SCORE || '0.5'),
      maxSearchLimit: parseInt(process.env.MAX_SEARCH_LIMIT || '50', 10),

      // Environment
      nodeEnv: (process.env.NODE_ENV || 'development') as 'development' | 'production' | 'test',
    };

    return ConfigSchema.parse(rawConfig);
  } catch (error) {
    if (error instanceof z.ZodError) {
      console.error('Configuration validation error:');
      error.errors.forEach((err) => {
        console.error(`  - ${err.path.join('.')}: ${err.message}`);
      });
      throw new Error('Invalid configuration. Please check your environment variables.');
    }
    throw error;
  }
}

/**
 * Application configuration
 */
export const appConfig = loadConfig();

/**
 * Get ChromaDB URL
 */
export function getChromaUrl(): string {
  return `http://${appConfig.chromaHost}:${appConfig.chromaPort}`;
}

/**
 * Check if running in production
 */
export function isProduction(): boolean {
  return appConfig.nodeEnv === 'production';
}

/**
 * Check if running in development
 */
export function isDevelopment(): boolean {
  return appConfig.nodeEnv === 'development';
}

/**
 * Check if running in test mode
 */
export function isTest(): boolean {
  return appConfig.nodeEnv === 'test';
}

export type AppConfig = z.infer<typeof ConfigSchema>;
