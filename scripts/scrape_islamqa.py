#!/usr/bin/env python3
"""
Script to scrape fatawa from IslamQA.info
Note: This is a basic scraper. For production, check robots.txt and rate limits.
"""

import requests
from bs4 import BeautifulSoup
import json
import time
from pathlib import Path
from typing import List, Dict, Optional
from tqdm import tqdm

# Output directory
OUTPUT_DIR = Path(__file__).parent.parent / 'data' / 'raw' / 'fatawa'

# Base URL
ISLAMQA_BASE = "https://islamqa.info/en/answers"

# Sample fatwa IDs to start with (in production, you'd crawl the site map)
# These are real fatwa IDs from islamqa.info
SAMPLE_FATWA_IDS = list(range(1, 100))  # Start with first 100


def fetch_fatwa(fatwa_id: int) -> Optional[Dict]:
    """Fetch a single fatwa from IslamQA"""
    url = f"{ISLAMQA_BASE}/{fatwa_id}"

    try:
        response = requests.get(url, timeout=30)

        # Skip if fatwa doesn't exist
        if response.status_code == 404:
            return None

        response.raise_for_status()

        # Parse HTML
        soup = BeautifulSoup(response.content, 'html.parser')

        # Extract question
        question_elem = soup.find('h1', class_='article-title')
        question = question_elem.get_text(strip=True) if question_elem else ''

        # Extract answer/ruling
        answer_elem = soup.find('div', class_='article-content')
        ruling = answer_elem.get_text(separator='\n', strip=True) if answer_elem else ''

        # Extract reference number
        ref_elem = soup.find('span', class_='article-number')
        ref_num = ref_elem.get_text(strip=True) if ref_elem else str(fatwa_id)

        # Extract topics/tags
        topics = []
        topic_elems = soup.find_all('a', class_='tag')
        for topic_elem in topic_elems:
            topics.append(topic_elem.get_text(strip=True).lower())

        # Build fatwa entry
        fatwa = {
            'id': f'islamqa_{fatwa_id}',
            'type': 'fatwa',
            'question': question,
            'ruling': ruling,
            'evidence': [],  # Evidence is embedded in the ruling text
            'source': {
                'title': 'IslamQA.info',
                'reference': f'Fatwa No. {ref_num}',
                'url': url,
                'scholar': 'IslamQA Scholars'
            },
            'topics': topics if topics else ['general'],
            'madhab': 'general',  # IslamQA doesn't always specify madhab
            'date': None,
        }

        return fatwa

    except requests.exceptions.RequestException as e:
        print(f"Error fetching fatwa {fatwa_id}: {e}")
        return None
    except Exception as e:
        print(f"Error parsing fatwa {fatwa_id}: {e}")
        return None


def scrape_fatawa(fatwa_ids: List[int]):
    """Scrape multiple fatawa"""
    print(f"\n{'='*60}")
    print(f"Scraping fatawa from IslamQA.info")
    print(f"{'='*60}")

    # Create output directory
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    fatawa = []
    failed = 0

    for fatwa_id in tqdm(fatwa_ids, desc="Scraping fatawa"):
        fatwa = fetch_fatwa(fatwa_id)

        if fatwa:
            fatawa.append(fatwa)
        else:
            failed += 1

        # Rate limiting - be respectful
        time.sleep(1.0)  # 1 second between requests

    # Save to JSON
    output_file = OUTPUT_DIR / 'islamqa_fatawa.json'
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(fatawa, f, ensure_ascii=False, indent=2)

    print(f"\n✓ Successfully scraped {len(fatawa)} fatawa")
    print(f"✗ Failed to fetch {failed} fatawa (likely don't exist)")
    print(f"Saved to: {output_file}")


def main():
    """Main function"""
    print("IslamQA.info Fatawa Scraper")
    print("NOTE: This is a basic demonstration scraper.")
    print("For production use:")
    print("  1. Check robots.txt and respect rate limits")
    print("  2. Crawl the sitemap for valid fatwa IDs")
    print("  3. Implement proper error handling and retries")
    print("  4. Consider reaching out to IslamQA for official API access")
    print()

    # Scrape sample fatawa
    scrape_fatawa(SAMPLE_FATWA_IDS)

    print("\n" + "="*60)
    print("Scraping completed!")
    print("="*60)


if __name__ == '__main__':
    main()
