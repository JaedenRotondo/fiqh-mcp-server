import { Source, FiqhEntry, Authenticity } from '../database/models.js';

/**
 * Format a source citation in Islamic scholarly format
 */
export function formatSourceCitation(source: Source, authenticity?: Authenticity): string {
  const parts: string[] = [];

  // Add the source title
  parts.push(source.title);

  // Add the reference
  if (source.reference) {
    parts.push(source.reference);
  }

  // Add scholar name if present (for fatawa)
  if (source.scholar) {
    parts.push(`by ${source.scholar}`);
  }

  // Add collection if present (for hadith)
  if (source.collection) {
    parts.push(`(${source.collection})`);
  }

  // Join all parts
  let citation = parts.join(', ');

  // Add authenticity grade for hadith
  if (authenticity && authenticity !== 'unknown') {
    citation += ` [${authenticity.charAt(0).toUpperCase() + authenticity.slice(1)}]`;
  }

  // Add URL if available
  if (source.url) {
    citation += `\nSource: ${source.url}`;
  }

  return citation;
}

/**
 * Format a complete fiqh entry for display
 */
export function formatFiqhEntry(entry: FiqhEntry, includeMetadata: boolean = true): string {
  const sections: string[] = [];

  // Question (for fatawa)
  if (entry.question) {
    sections.push(`**Question:** ${entry.question}\n`);
  }

  // Ruling/Content
  sections.push(`**Ruling:**`);
  sections.push(entry.ruling);
  sections.push('');

  // Evidence
  if (entry.evidence && entry.evidence.length > 0) {
    sections.push(`**Evidence:**`);
    entry.evidence.forEach((evidence, index) => {
      sections.push(`${index + 1}. ${evidence}`);
    });
    sections.push('');
  }

  // Metadata
  if (includeMetadata) {
    const metadata: string[] = [];

    if (entry.madhab) {
      metadata.push(`**Madhab:** ${capitalizeFirstLetter(entry.madhab)}`);
    }

    if (entry.topics && entry.topics.length > 0) {
      metadata.push(`**Topics:** ${entry.topics.map(capitalizeFirstLetter).join(', ')}`);
    }

    if (entry.type) {
      metadata.push(`**Type:** ${capitalizeFirstLetter(entry.type.replace('_', ' '))}`);
    }

    if (metadata.length > 0) {
      sections.push(metadata.join(' | '));
      sections.push('');
    }
  }

  // Source citation
  sections.push(`**Source:** ${formatSourceCitation(entry.source, entry.authenticity)}`);

  return sections.join('\n');
}

/**
 * Format multiple entries as a numbered list
 */
export function formatMultipleEntries(entries: FiqhEntry[]): string {
  if (entries.length === 0) {
    return 'No results found.';
  }

  const formatted = entries.map((entry, index) => {
    return `\n### Result ${index + 1}\n\n${formatFiqhEntry(entry)}`;
  });

  return formatted.join('\n\n---\n');
}

/**
 * Create a summary of search results
 */
export function createResultsSummary(entries: FiqhEntry[], query: string): string {
  const summary: string[] = [];

  summary.push(`Found ${entries.length} result(s) for: "${query}"\n`);

  // Group by madhab
  const byMadhab = groupByMadhab(entries);
  if (Object.keys(byMadhab).length > 1) {
    summary.push(`**Results by Madhab:**`);
    Object.entries(byMadhab).forEach(([madhab, count]) => {
      summary.push(`- ${capitalizeFirstLetter(madhab)}: ${count}`);
    });
    summary.push('');
  }

  // Group by type
  const byType = groupByType(entries);
  if (Object.keys(byType).length > 1) {
    summary.push(`**Results by Type:**`);
    Object.entries(byType).forEach(([type, count]) => {
      summary.push(`- ${capitalizeFirstLetter(type.replace('_', ' '))}: ${count}`);
    });
    summary.push('');
  }

  return summary.join('\n');
}

/**
 * Group entries by madhab
 */
function groupByMadhab(entries: FiqhEntry[]): Record<string, number> {
  const groups: Record<string, number> = {};
  entries.forEach((entry) => {
    const madhab = entry.madhab || 'general';
    groups[madhab] = (groups[madhab] || 0) + 1;
  });
  return groups;
}

/**
 * Group entries by type
 */
function groupByType(entries: FiqhEntry[]): Record<string, number> {
  const groups: Record<string, number> = {};
  entries.forEach((entry) => {
    groups[entry.type] = (groups[entry.type] || 0) + 1;
  });
  return groups;
}

/**
 * Capitalize first letter of a string
 */
function capitalizeFirstLetter(str: string): string {
  return str.charAt(0).toUpperCase() + str.slice(1);
}

/**
 * Truncate text to a maximum length
 */
export function truncateText(text: string, maxLength: number): string {
  if (text.length <= maxLength) {
    return text;
  }
  return text.substring(0, maxLength - 3) + '...';
}

/**
 * Format authenticity grade with emoji indicators
 */
export function formatAuthenticity(authenticity?: Authenticity): string {
  if (!authenticity || authenticity === 'unknown') {
    return '';
  }

  const grades: Record<Authenticity, string> = {
    sahih: '✓ Sahih (Authentic)',
    hasan: '~ Hasan (Good)',
    daif: '✗ Daif (Weak)',
    mawdu: '✗✗ Mawdu (Fabricated)',
    unknown: '',
  };

  return grades[authenticity];
}
