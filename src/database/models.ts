import { z } from 'zod';

/**
 * Madhab (Islamic school of jurisprudence)
 */
export const MadhabSchema = z.enum(['hanafi', 'maliki', 'shafi', 'hanbali', 'general']);
export type Madhab = z.infer<typeof MadhabSchema>;

/**
 * Type of fiqh entry
 */
export const FiqhEntryTypeSchema = z.enum(['hadith', 'fatwa', 'classical_text']);
export type FiqhEntryType = z.infer<typeof FiqhEntryTypeSchema>;

/**
 * Authenticity grade for hadith
 */
export const AuthenticitySchema = z.enum(['sahih', 'hasan', 'daif', 'mawdu', 'unknown']);
export type Authenticity = z.infer<typeof AuthenticitySchema>;

/**
 * Source information for a fiqh entry
 */
export const SourceSchema = z.object({
  title: z.string().describe('Title of the source (e.g., "Sahih Bukhari")'),
  reference: z.string().describe('Specific reference within the source (e.g., "Book 2, Hadith 123")'),
  url: z.string().url().optional().describe('URL to the source if available'),
  scholar: z.string().optional().describe('Scholar name for fatawa'),
  collection: z.string().optional().describe('Collection name for hadith (e.g., "Kutub al-Sittah")'),
});
export type Source = z.infer<typeof SourceSchema>;

/**
 * Complete fiqh entry structure
 */
export const FiqhEntrySchema = z.object({
  id: z.string().describe('Unique identifier for the entry'),
  type: FiqhEntryTypeSchema.describe('Type of entry: hadith, fatwa, or classical text'),
  question: z.string().optional().describe('Original question for fatawa'),
  ruling: z.string().describe('The actual fiqh ruling or hadith text'),
  evidence: z.array(z.string()).describe('Supporting evidence (Quran verses, hadith references)'),
  source: SourceSchema.describe('Source attribution and citation'),
  madhab: MadhabSchema.optional().describe('School of thought this ruling belongs to'),
  topics: z.array(z.string()).describe('Topic tags (e.g., ["prayer", "wudu", "purification"])'),
  authenticity: AuthenticitySchema.optional().describe('Authenticity grade for hadith'),
  date: z.string().optional().describe('Date for contemporary fatawa (ISO format)'),
  arabicText: z.string().optional().describe('Original Arabic text if available'),
  transliteration: z.string().optional().describe('Transliteration for hadith'),
});
export type FiqhEntry = z.infer<typeof FiqhEntrySchema>;

/**
 * Search result with similarity score
 */
export const SearchResultSchema = z.object({
  entry: FiqhEntrySchema,
  score: z.number().describe('Similarity score (0-1)'),
  distance: z.number().optional().describe('Distance metric from vector search'),
});
export type SearchResult = z.infer<typeof SearchResultSchema>;

/**
 * Query parameters for fiqh search
 */
export const QueryParamsSchema = z.object({
  query: z.string().describe('The search query'),
  madhab: MadhabSchema.optional().describe('Filter by specific madhab'),
  type: FiqhEntryTypeSchema.optional().describe('Filter by entry type'),
  topics: z.array(z.string()).optional().describe('Filter by topics'),
  limit: z.number().min(1).max(50).default(5).describe('Maximum number of results'),
  minScore: z.number().min(0).max(1).default(0.5).describe('Minimum similarity score'),
});
export type QueryParams = z.infer<typeof QueryParamsSchema>;

/**
 * Browse parameters for topic/madhab browsing
 */
export const BrowseParamsSchema = z.object({
  topic: z.string().optional().describe('Topic to browse'),
  madhab: MadhabSchema.optional().describe('Madhab to filter by'),
  limit: z.number().min(1).max(100).default(20).describe('Maximum number of results'),
  offset: z.number().min(0).default(0).describe('Pagination offset'),
});
export type BrowseParams = z.infer<typeof BrowseParamsSchema>;

/**
 * Reference lookup parameters
 */
export const ReferenceParamsSchema = z.object({
  source: z.string().describe('Source title (e.g., "Sahih Bukhari")'),
  reference: z.string().describe('Specific reference (e.g., "Book 2, Hadith 123")'),
});
export type ReferenceParams = z.infer<typeof ReferenceParamsSchema>;

/**
 * Statistics about the fiqh database
 */
export const DatabaseStatsSchema = z.object({
  totalEntries: z.number(),
  entriesByType: z.record(FiqhEntryTypeSchema, z.number()),
  entriesByMadhab: z.record(MadhabSchema, z.number()),
  totalTopics: z.number(),
  totalScholars: z.number(),
});
export type DatabaseStats = z.infer<typeof DatabaseStatsSchema>;

/**
 * Topic with entry count
 */
export const TopicInfoSchema = z.object({
  name: z.string(),
  count: z.number(),
  madhabs: z.array(MadhabSchema).optional(),
});
export type TopicInfo = z.infer<typeof TopicInfoSchema>;

/**
 * Scholar with entry count
 */
export const ScholarInfoSchema = z.object({
  name: z.string(),
  count: z.number(),
  madhab: MadhabSchema.optional(),
  period: z.string().optional().describe('Time period (e.g., "Contemporary", "Classical")'),
});
export type ScholarInfo = z.infer<typeof ScholarInfoSchema>;
