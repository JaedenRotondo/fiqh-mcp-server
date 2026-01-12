import { Server } from '@modelcontextprotocol/sdk/server/index.js';
import { StdioServerTransport } from '@modelcontextprotocol/sdk/server/stdio.js';
import {
  CallToolRequestSchema,
  ListToolsRequestSchema,
} from '@modelcontextprotocol/sdk/types.js';
import { semanticSearch, getByTopic, getByReference, getAllTopics, getAllScholars, getDatabaseStats } from './search/vector-search.js';
import { QueryParamsSchema, MadhabSchema } from './database/models.js';
import { formatFiqhEntry, formatMultipleEntries, createResultsSummary } from './utils/source-formatter.js';

/**
 * Create and configure the MCP server
 */
export function createServer(): Server {
  const server = new Server(
    {
      name: 'fiqh-mcp-server',
      version: '1.0.0',
    },
    {
      capabilities: {
        tools: {},
      },
    }
  );

  /**
   * List available tools
   */
  server.setRequestHandler(ListToolsRequestSchema, async () => {
    return {
      tools: [
        {
          name: 'query_fiqh',
          description: 'Search for Islamic fiqh rulings using semantic AI-powered search. Returns relevant rulings from hadith, fatawa, and classical texts with proper source citations.',
          inputSchema: {
            type: 'object',
            properties: {
              query: {
                type: 'string',
                description: 'The question or topic to search for (e.g., "What is the ruling on combining prayers while traveling?")',
              },
              madhab: {
                type: 'string',
                enum: ['hanafi', 'maliki', 'shafi', 'hanbali', 'general'],
                description: 'Optional: Filter by specific school of thought (madhab)',
              },
              limit: {
                type: 'number',
                description: 'Maximum number of results to return (default: 5, max: 50)',
                minimum: 1,
                maximum: 50,
              },
            },
            required: ['query'],
          },
        },
        {
          name: 'browse_by_topic',
          description: 'Browse fiqh rulings by topic category (e.g., prayer, fasting, zakat)',
          inputSchema: {
            type: 'object',
            properties: {
              topic: {
                type: 'string',
                description: 'The topic to browse (e.g., "prayer", "wudu", "zakat")',
              },
              madhab: {
                type: 'string',
                enum: ['hanafi', 'maliki', 'shafi', 'hanbali', 'general'],
                description: 'Optional: Filter by specific school of thought',
              },
              limit: {
                type: 'number',
                description: 'Maximum number of results (default: 20)',
                minimum: 1,
                maximum: 100,
              },
            },
            required: ['topic'],
          },
        },
        {
          name: 'get_ruling_by_reference',
          description: 'Get a specific hadith or fatwa by its source reference (e.g., "Sahih Bukhari, Book 2, Hadith 123")',
          inputSchema: {
            type: 'object',
            properties: {
              source: {
                type: 'string',
                description: 'The source title (e.g., "Sahih Bukhari", "IslamQA")',
              },
              reference: {
                type: 'string',
                description: 'The specific reference (e.g., "Book 2, Hadith 123", "Fatwa No. 12345")',
              },
            },
            required: ['source', 'reference'],
          },
        },
        {
          name: 'list_topics',
          description: 'List all available fiqh topics with entry counts',
          inputSchema: {
            type: 'object',
            properties: {},
          },
        },
        {
          name: 'list_scholars',
          description: 'List all scholars in the database with entry counts',
          inputSchema: {
            type: 'object',
            properties: {},
          },
        },
        {
          name: 'get_database_stats',
          description: 'Get statistics about the fiqh database (total entries, breakdown by type and madhab)',
          inputSchema: {
            type: 'object',
            properties: {},
          },
        },
      ],
    };
  });

  /**
   * Handle tool calls
   */
  server.setRequestHandler(CallToolRequestSchema, async (request) => {
    const { name, arguments: args } = request.params;

    try {
      switch (name) {
        case 'query_fiqh': {
          // Validate and parse arguments
          const params = QueryParamsSchema.parse(args);

          // Perform semantic search
          const results = await semanticSearch(params);

          if (results.length === 0) {
            return {
              content: [
                {
                  type: 'text',
                  text: `No results found for: "${params.query}"\n\nTry:\n- Using different keywords\n- Broadening your search\n- Checking the spelling`,
                },
              ],
            };
          }

          // Format results
          const entries = results.map(r => r.entry);
          const summary = createResultsSummary(entries, params.query);
          const formattedResults = formatMultipleEntries(entries);

          return {
            content: [
              {
                type: 'text',
                text: `${summary}\n${formattedResults}`,
              },
            ],
          };
        }

        case 'browse_by_topic': {
          const topic = String(args?.topic);
          const madhab = args?.madhab ? MadhabSchema.parse(args.madhab) : undefined;
          const limit = Number(args?.limit) || 20;

          const entries = await getByTopic(topic, madhab, limit);

          if (entries.length === 0) {
            return {
              content: [
                {
                  type: 'text',
                  text: `No entries found for topic: "${topic}"${madhab ? ` in ${madhab} madhab` : ''}`,
                },
              ],
            };
          }

          const formatted = formatMultipleEntries(entries);

          return {
            content: [
              {
                type: 'text',
                text: `Found ${entries.length} entries for topic: "${topic}"${madhab ? ` (${madhab} madhab)` : ''}\n\n${formatted}`,
              },
            ],
          };
        }

        case 'get_ruling_by_reference': {
          const source = String(args?.source);
          const reference = String(args?.reference);

          const entry = await getByReference(source, reference);

          if (!entry) {
            return {
              content: [
                {
                  type: 'text',
                  text: `No entry found for: ${source}, ${reference}`,
                },
              ],
            };
          }

          const formatted = formatFiqhEntry(entry, true);

          return {
            content: [
              {
                type: 'text',
                text: formatted,
              },
            ],
          };
        }

        case 'list_topics': {
          const topics = getAllTopics();

          const topicList = topics
            .slice(0, 50) // Limit to top 50
            .map(t => `- ${t.name} (${t.count} entries)`)
            .join('\n');

          return {
            content: [
              {
                type: 'text',
                text: `**Available Topics** (showing top 50):\n\n${topicList}\n\nTotal topics: ${topics.length}`,
              },
            ],
          };
        }

        case 'list_scholars': {
          const scholars = getAllScholars();

          if (scholars.length === 0) {
            return {
              content: [
                {
                  type: 'text',
                  text: 'No scholars found in the database.',
                },
              ],
            };
          }

          const scholarList = scholars
            .map(s => `- ${s.name} (${s.count} entries)`)
            .join('\n');

          return {
            content: [
              {
                type: 'text',
                text: `**Scholars in Database:**\n\n${scholarList}`,
              },
            ],
          };
        }

        case 'get_database_stats': {
          const stats = getDatabaseStats();

          const statsText = [
            '**Fiqh Database Statistics**\n',
            `Total Entries: ${stats.totalEntries}`,
            '',
            '**Entries by Type:**',
            ...Object.entries(stats.entriesByType).map(([type, count]) => `- ${type}: ${count}`),
            '',
            '**Entries by Madhab:**',
            ...Object.entries(stats.entriesByMadhab).map(([madhab, count]) => `- ${madhab}: ${count}`),
            '',
            `Total Topics: ${stats.totalTopics}`,
            `Total Scholars: ${stats.totalScholars}`,
          ].join('\n');

          return {
            content: [
              {
                type: 'text',
                text: statsText,
              },
            ],
          };
        }

        default:
          throw new Error(`Unknown tool: ${name}`);
      }
    } catch (error) {
      console.error(`Error executing tool ${name}:`, error);

      return {
        content: [
          {
            type: 'text',
            text: `Error: ${error instanceof Error ? error.message : 'Unknown error occurred'}`,
          },
        ],
        isError: true,
      };
    }
  });

  return server;
}

/**
 * Run the MCP server
 */
export async function runServer(): Promise<void> {
  const server = createServer();
  const transport = new StdioServerTransport();

  await server.connect(transport);

  console.error('Fiqh MCP Server running on stdio');
}
