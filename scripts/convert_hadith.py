#!/usr/bin/env python3
"""
Convert AhmedBaset hadith-json dataset to FiqhEntry schema
"""

import json
import os
from pathlib import Path
from typing import Dict, List, Any
from tqdm import tqdm

# Paths
BASE_DIR = Path(__file__).parent.parent
HADITH_DIR = BASE_DIR / 'temp_hadith_ahmed' / 'db' / 'by_book' / 'the_9_books'
OUTPUT_DIR = BASE_DIR / 'data' / 'raw' / 'hadith'

# Collection metadata
COLLECTION_INFO = {
    'bukhari': {
        'english_name': 'Sahih al-Bukhari',
        'arabic_name': 'صحيح البخاري',
        'author': 'Imam Muhammad ibn Ismail al-Bukhari',
        'authenticity': 'sahih',
        'collection': 'Kutub al-Sittah',
        'url_base': 'https://sunnah.com/bukhari'
    },
    'muslim': {
        'english_name': 'Sahih Muslim',
        'arabic_name': 'صحيح مسلم',
        'author': 'Imam Muslim ibn al-Hajjaj',
        'authenticity': 'sahih',
        'collection': 'Kutub al-Sittah',
        'url_base': 'https://sunnah.com/muslim'
    },
    'abudawud': {
        'english_name': 'Sunan Abi Dawud',
        'arabic_name': 'سنن أبي داود',
        'author': 'Imam Abu Dawud al-Sijistani',
        'authenticity': 'unknown',
        'collection': 'Kutub al-Sittah',
        'url_base': 'https://sunnah.com/abudawud'
    },
    'tirmidhi': {
        'english_name': 'Jami at-Tirmidhi',
        'arabic_name': 'جامع الترمذي',
        'author': 'Imam at-Tirmidhi',
        'authenticity': 'unknown',
        'collection': 'Kutub al-Sittah',
        'url_base': 'https://sunnah.com/tirmidhi'
    },
    'nasai': {
        'english_name': 'Sunan an-Nasa\'i',
        'arabic_name': 'سنن النسائي',
        'author': 'Imam an-Nasa\'i',
        'authenticity': 'unknown',
        'collection': 'Kutub al-Sittah',
        'url_base': 'https://sunnah.com/nasai'
    },
    'ibnmajah': {
        'english_name': 'Sunan Ibn Majah',
        'arabic_name': 'سنن ابن ماجه',
        'author': 'Imam Ibn Majah',
        'authenticity': 'unknown',
        'collection': 'Kutub al-Sittah',
        'url_base': 'https://sunnah.com/ibnmajah'
    },
    'ahmed': {
        'english_name': 'Musnad Ahmad',
        'arabic_name': 'مسند أحمد',
        'author': 'Imam Ahmad ibn Hanbal',
        'authenticity': 'unknown',
        'collection': 'Nine Books',
        'url_base': 'https://sunnah.com/ahmad'
    },
    'darimi': {
        'english_name': 'Sunan ad-Darimi',
        'arabic_name': 'سنن الدارمي',
        'author': 'Imam ad-Darimi',
        'authenticity': 'unknown',
        'collection': 'Nine Books',
        'url_base': 'https://sunnah.com/darimi'
    },
    'malik': {
        'english_name': 'Muwatta Malik',
        'arabic_name': 'موطأ مالك',
        'author': 'Imam Malik ibn Anas',
        'authenticity': 'unknown',
        'collection': 'Nine Books',
        'url_base': 'https://sunnah.com/malik'
    }
}


def extract_topics_from_chapter(chapter_name: str) -> List[str]:
    """Extract topic tags from chapter name"""
    if not chapter_name:
        return ['general']

    # Convert to lowercase and clean
    chapter_lower = chapter_name.lower()

    # Topic mapping
    topic_keywords = {
        'prayer': ['prayer', 'salah', 'salat', 'praying'],
        'fasting': ['fasting', 'fast', 'sawm', 'ramadan'],
        'zakat': ['zakat', 'charity', 'alms'],
        'hajj': ['hajj', 'pilgrimage', 'umrah'],
        'purification': ['purification', 'wudu', 'ablution', 'ghusl', 'tayammum'],
        'faith': ['faith', 'belief', 'iman', 'creed'],
        'marriage': ['marriage', 'nikah', 'divorce', 'talaq'],
        'trade': ['trade', 'business', 'transactions', 'buying', 'selling'],
        'food': ['food', 'drink', 'eating', 'slaughtering'],
        'clothing': ['clothing', 'dress', 'garment'],
        'funeral': ['funeral', 'burial', 'death', 'janazah'],
        'jihad': ['jihad', 'fighting', 'warfare'],
        'knowledge': ['knowledge', 'learning', 'teaching'],
        'manners': ['manners', 'adab', 'etiquette', 'behavior'],
    }

    topics = []
    for topic, keywords in topic_keywords.items():
        if any(keyword in chapter_lower for keyword in keywords):
            topics.append(topic)

    # If no topics found, use 'general'
    return topics if topics else ['general']


def convert_hadith(hadith: Dict, collection_key: str, chapters_map: Dict) -> Dict:
    """Convert a single hadith to FiqhEntry format"""
    collection = COLLECTION_INFO[collection_key]

    # Get chapter info for topics
    chapter_id = hadith.get('chapterId')
    chapter = chapters_map.get(chapter_id, {})
    chapter_name = chapter.get('english', '')

    # Extract topics
    topics = extract_topics_from_chapter(chapter_name)

    # Build narrator and text
    english_data = hadith.get('english', {})
    narrator = english_data.get('narrator', '')
    text = english_data.get('text', '')

    # Combine for ruling field
    if narrator and text:
        ruling = f"{narrator}\n\n{text}"
    else:
        ruling = text or hadith.get('arabic', '')

    # Build reference
    book_id = hadith.get('bookId', '?')
    hadith_num = hadith.get('idInBook', hadith.get('id', '?'))
    reference = f"Book {book_id}, Hadith {hadith_num}"

    # Build URL
    url = f"{collection['url_base']}/{hadith_num}"

    # Build FiqhEntry
    entry = {
        'id': f"{collection_key}_{hadith.get('id', hadith_num)}",
        'type': 'hadith',
        'ruling': ruling.strip(),
        'evidence': [],  # Hadith themselves are evidence
        'source': {
            'title': collection['english_name'],
            'reference': reference,
            'url': url,
            'collection': collection['collection']
        },
        'madhab': 'general',  # Hadith not specific to madhab
        'topics': topics,
        'authenticity': collection['authenticity'],
        'arabicText': hadith.get('arabic', ''),
    }

    return entry


def process_collection(collection_key: str) -> List[Dict]:
    """Process a single hadith collection"""
    json_file = HADITH_DIR / f"{collection_key}.json"

    if not json_file.exists():
        print(f"Warning: {json_file} not found, skipping")
        return []

    print(f"\nProcessing {collection_key}...")

    try:
        with open(json_file, 'r', encoding='utf-8') as f:
            data = json.load(f)

        # Get metadata
        metadata = data.get('metadata', {})
        hadith_count = metadata.get('length', 0)
        print(f"Found {hadith_count} hadiths in {collection_key}")

        # Build chapters map for topic extraction
        chapters_map = {}
        for chapter in data.get('chapters', []):
            chapters_map[chapter['id']] = chapter

        # Convert all hadiths
        entries = []
        hadiths = data.get('hadiths', [])

        for hadith in tqdm(hadiths, desc=f"Converting {collection_key}"):
            try:
                entry = convert_hadith(hadith, collection_key, chapters_map)
                if entry['ruling']:  # Only include if we have text
                    entries.append(entry)
            except Exception as e:
                print(f"\nError converting hadith {hadith.get('id')}: {e}")
                continue

        print(f"✓ Converted {len(entries)} hadiths from {collection_key}")
        return entries

    except Exception as e:
        print(f"Error processing {collection_key}: {e}")
        return []


def main():
    """Main conversion function"""
    print("="*60)
    print("Hadith Dataset Converter")
    print("Converting AhmedBaset hadith-json to FiqhEntry schema")
    print("="*60)

    # Create output directory
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    # Process all collections
    all_entries = []

    for collection_key in COLLECTION_INFO.keys():
        entries = process_collection(collection_key)
        all_entries.extend(entries)

    # Save combined output
    output_file = OUTPUT_DIR / 'all_hadith.json'
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(all_entries, f, ensure_ascii=False, indent=2)

    print("\n" + "="*60)
    print("Conversion Complete!")
    print("="*60)
    print(f"Total hadiths converted: {len(all_entries)}")
    print(f"Output file: {output_file}")
    print(f"File size: {output_file.stat().st_size / (1024*1024):.1f} MB")

    # Print statistics
    print("\nBreakdown by collection:")
    collection_counts = {}
    for entry in all_entries:
        source = entry['source']['title']
        collection_counts[source] = collection_counts.get(source, 0) + 1

    for collection, count in sorted(collection_counts.items()):
        print(f"  {collection}: {count}")


if __name__ == '__main__':
    main()
