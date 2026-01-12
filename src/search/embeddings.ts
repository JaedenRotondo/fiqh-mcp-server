import OpenAI from 'openai';
import { appConfig } from '../utils/config.js';

/**
 * OpenAI client instance
 */
let openaiClient: OpenAI | null = null;

/**
 * Get or create OpenAI client
 */
function getOpenAIClient(): OpenAI {
  if (!openaiClient) {
    openaiClient = new OpenAI({
      apiKey: appConfig.openaiApiKey,
    });
  }
  return openaiClient;
}

/**
 * Generate embedding for a single text
 */
export async function generateEmbedding(text: string): Promise<number[]> {
  const client = getOpenAIClient();

  try {
    const response = await client.embeddings.create({
      model: appConfig.embeddingModel,
      input: text,
    });

    return response.data[0].embedding;
  } catch (error) {
    console.error('Error generating embedding:', error);
    throw new Error(`Failed to generate embedding: ${error instanceof Error ? error.message : 'Unknown error'}`);
  }
}

/**
 * Generate embeddings for multiple texts (batch)
 */
export async function generateEmbeddings(texts: string[]): Promise<number[][]> {
  const client = getOpenAIClient();

  try {
    const response = await client.embeddings.create({
      model: appConfig.embeddingModel,
      input: texts,
    });

    return response.data.map(item => item.embedding);
  } catch (error) {
    console.error('Error generating embeddings:', error);
    throw new Error(`Failed to generate embeddings: ${error instanceof Error ? error.message : 'Unknown error'}`);
  }
}
