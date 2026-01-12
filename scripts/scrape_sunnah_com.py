#!/usr/bin/env python3
"""
Script to fetch hadith data from sunnah.com API
Sunnah.com provides free access to authenticated hadith collections
"""

import requests
import json
import os
from pathlib import Path
from typing import List, Dict, Any
from tqdm import tqdm
import time

# API Base URL
SUNNAH_API_BASE = "https://api.sunnah.com/v1"

# Collections to fetch (with their API collection names)
COLLECTIONS = {
    'bukhari': 'sahih-bukhari',
    'muslim': 'sahih-muslim',
    'abudawud': 'sunan-abi-dawud',
    'tirmidhi': 'jami-at-tirmidhi',
    'nasai': 'sunan-an-nasai',
    'ibnmajah': 'sunan-ibn-majah',
}

# Output directory
OUTPUT_DIR = Path(__file__).parent.parent / 'data' / 'raw' / 'hadith'


def fetch_collection_books(collection_name: str, api_key: str) -> List[Dict]:
    """Fetch the list of books in a collection"""
    url = f"{SUNNAH_API_BASE}/collections/{collection_name}/books"
    headers = {'X-API-Key': api_key} if api_key else {}

    try:
        response = requests.get(url, headers=headers, timeout=30)
        response.raise_for_status()
        data = response.json()
        return data.get('data', [])
    except requests.exceptions.RequestException as e:
        print(f"Error fetching books for {collection_name}: {e}")
        return []


def fetch_book_hadiths(collection_name: str, book_number: int, api_key: str) -> List[Dict]:
    """Fetch all hadiths from a specific book"""
    url = f"{SUNNAH_API_BASE}/collections/{collection_name}/books/{book_number}/hadiths"
    headers = {'X-API-Key': api_key} if api_key else {}

    try:
        response = requests.get(url, headers=headers, timeout=30)
        response.raise_for_status()
        data = response.json()
        return data.get('data', [])
    except requests.exceptions.RequestException as e:
        print(f"Error fetching hadiths for {collection_name} book {book_number}: {e}")
        return []


def extract_hadith_info(hadith: Dict, collection_key: str, collection_name: str) -> Dict:
    """Extract relevant information from hadith data"""
    return {
        'id': f"{collection_key}_{hadith.get('hadithNumber', 'unknown')}",
        'type': 'hadith',
        'ruling': hadith.get('hadithEnglish', {}).get('body', ''),
        'arabicText': hadith.get('hadithArabic', {}).get('body', ''),
        'source': {
            'title': collection_name.replace('-', ' ').title(),
            'reference': f"Book {hadith.get('bookNumber', '?')}, Hadith {hadith.get('hadithNumber', '?')}",
            'collection': 'Kutub al-Sittah',
            'url': f"https://sunnah.com/{collection_name}/{hadith.get('hadithNumber', '')}"
        },
        'authenticity': determine_authenticity(collection_key, hadith),
        'topics': extract_topics(hadith),
        'narrator': hadith.get('hadithEnglish', {}).get('chapterName', ''),
        'bookNumber': hadith.get('bookNumber'),
        'hadithNumber': hadith.get('hadithNumber'),
        'grades': hadith.get('grades', []),
    }


def determine_authenticity(collection_key: str, hadith: Dict) -> str:
    """Determine authenticity grade based on collection and grades"""
    # Sahih Bukhari and Sahih Muslim are considered sahih by default
    if collection_key in ['bukhari', 'muslim']:
        return 'sahih'

    # Check explicit grades
    grades = hadith.get('grades', [])
    if grades:
        for grade in grades:
            grade_text = grade.get('grade', '').lower()
            if 'sahih' in grade_text:
                return 'sahih'
            elif 'hasan' in grade_text:
                return 'hasan'
            elif 'daif' in grade_text or 'weak' in grade_text:
                return 'daif'

    return 'unknown'


def extract_topics(hadith: Dict) -> List[str]:
    """Extract topic tags from hadith metadata"""
    topics = []

    # Add chapter name as a topic
    chapter = hadith.get('hadithEnglish', {}).get('chapterName', '')
    if chapter:
        # Clean and split chapter name into topics
        chapter_topics = chapter.lower().replace('chapter:', '').strip()
        if chapter_topics:
            topics.append(chapter_topics)

    # Add book name as a broader topic
    book_name = hadith.get('bookName', '')
    if book_name:
        topics.append(book_name.lower().strip())

    return list(set(topics))  # Remove duplicates


def scrape_collection(collection_key: str, collection_name: str, api_key: str):
    """Scrape an entire hadith collection"""
    print(f"\n{'='*60}")
    print(f"Scraping {collection_name}")
    print(f"{'='*60}")

    # Create collection directory
    collection_dir = OUTPUT_DIR / collection_key
    collection_dir.mkdir(parents=True, exist_ok=True)

    # Fetch books in the collection
    print(f"Fetching books list...")
    books = fetch_collection_books(collection_name, api_key)

    if not books:
        print(f"No books found for {collection_name}")
        return

    print(f"Found {len(books)} books in {collection_name}")

    all_hadiths = []

    # Fetch hadiths from each book
    for book in tqdm(books, desc="Processing books"):
        book_number = book.get('bookNumber')
        if not book_number:
            continue

        # Fetch hadiths
        hadiths = fetch_book_hadiths(collection_name, book_number, api_key)

        # Process each hadith
        for hadith in hadiths:
            try:
                hadith_info = extract_hadith_info(hadith, collection_key, collection_name)
                if hadith_info['ruling']:  # Only save if we have text
                    all_hadiths.append(hadith_info)
            except Exception as e:
                print(f"Error processing hadith: {e}")
                continue

        # Rate limiting - be respectful to the API
        time.sleep(0.5)

    # Save to JSON file
    output_file = collection_dir / f"{collection_key}_hadiths.json"
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(all_hadiths, f, ensure_ascii=False, indent=2)

    print(f"✓ Saved {len(all_hadiths)} hadiths to {output_file}")


def main():
    """Main function to scrape all collections"""
    # Get API key from environment variable (optional but recommended)
    api_key = os.getenv('SUNNAH_API_KEY', '')

    if not api_key:
        print("Warning: No SUNNAH_API_KEY found in environment.")
        print("You can still use the API, but may have rate limits.")
        print("Get a free API key at: https://sunnah.api-docs.io/")
        print()

    # Create output directory
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    print("Starting hadith collection from Sunnah.com")
    print(f"Output directory: {OUTPUT_DIR}")
    print(f"Collections to scrape: {list(COLLECTIONS.keys())}")

    # Scrape each collection
    for collection_key, collection_name in COLLECTIONS.items():
        try:
            scrape_collection(collection_key, collection_name, api_key)
        except Exception as e:
            print(f"Error scraping {collection_name}: {e}")
            continue

    print("\n" + "="*60)
    print("Hadith scraping completed!")
    print("="*60)


if __name__ == '__main__':
    main()
