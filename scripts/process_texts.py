#!/usr/bin/env python3
"""
Script to process and unify fiqh data from various sources
Cleans, validates, and combines hadith and fatawa into a single database
"""

import json
import re
from pathlib import Path
from typing import List, Dict, Any
from tqdm import tqdm
import uuid

# Paths
RAW_DATA_DIR = Path(__file__).parent.parent / 'data' / 'raw'
PROCESSED_DATA_DIR = Path(__file__).parent.parent / 'data' / 'processed'
OUTPUT_FILE = PROCESSED_DATA_DIR / 'fiqh_database.json'
SOURCES_FILE = PROCESSED_DATA_DIR / 'sources.json'


def clean_text(text: str) -> str:
    """Clean and normalize text"""
    if not text:
        return ""

    # Remove excessive whitespace
    text = re.sub(r'\s+', ' ', text)

    # Remove HTML entities
    text = text.replace('&nbsp;', ' ')
    text = text.replace('&quot;', '"')
    text = text.replace('&amp;', '&')
    text = text.replace('&lt;', '<')
    text = text.replace('&gt;', '>')

    # Remove remaining HTML tags
    text = re.sub(r'<[^>]+>', '', text)

    # Normalize quotes
    text = text.replace('"', '"').replace('"', '"')
    text = text.replace(''', "'").replace(''', "'")

    # Trim
    text = text.strip()

    return text


def extract_evidence_from_text(text: str) -> List[str]:
    """Extract Quran and hadith references from text"""
    evidence = []

    # Look for Quran references
    quran_patterns = [
        r'(?:Surah|Chapter)\s+[\w-]+\s*[:,]\s*(?:Ayah|Verse)\s+\d+',
        r'(?:Quran|Al-Quran)\s+\d+:\d+',
        r'\[\d+:\d+\]'
    ]

    for pattern in quran_patterns:
        matches = re.finditer(pattern, text, re.IGNORECASE)
        for match in matches:
            evidence.append(clean_text(match.group()))

    # Look for hadith references
    hadith_patterns = [
        r'(?:Bukhari|Muslim|Tirmidhi|Abu Dawud|Ibn Majah|Nasai)\s+\d+',
        r'Sahih\s+(?:Bukhari|Muslim)',
    ]

    for pattern in hadith_patterns:
        matches = re.finditer(pattern, text, re.IGNORECASE)
        for match in matches:
            evidence.append(clean_text(match.group()))

    return list(set(evidence))  # Remove duplicates


def normalize_topic(topic: str) -> str:
    """Normalize topic names"""
    topic = topic.lower().strip()

    # Common normalizations
    normalizations = {
        'salah': 'prayer',
        'salat': 'prayer',
        'namaz': 'prayer',
        'salaah': 'prayer',
        'wudhu': 'wudu',
        'wudoo': 'wudu',
        'zakah': 'zakat',
        'zakaah': 'zakat',
        'sawm': 'fasting',
        'siyam': 'fasting',
        'hajj': 'pilgrimage',
        'nikah': 'marriage',
        'talaaq': 'divorce',
        'talaq': 'divorce',
    }

    return normalizations.get(topic, topic)


def process_hadith_file(file_path: Path) -> List[Dict]:
    """Process a hadith JSON file"""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            hadiths = json.load(f)

        processed = []
        for hadith in hadiths:
            # Clean ruling text
            ruling = clean_text(hadith.get('ruling', ''))
            if not ruling or len(ruling) < 20:  # Skip very short entries
                continue

            # Process topics
            topics = [normalize_topic(t) for t in hadith.get('topics', [])]
            if not topics:
                topics = ['general']

            # Extract additional evidence if not present
            evidence = hadith.get('evidence', [])
            if not evidence:
                evidence = extract_evidence_from_text(ruling)

            processed_hadith = {
                'id': hadith.get('id', str(uuid.uuid4())),
                'type': 'hadith',
                'ruling': ruling,
                'arabicText': clean_text(hadith.get('arabicText', '')),
                'evidence': evidence,
                'source': hadith.get('source', {}),
                'authenticity': hadith.get('authenticity', 'unknown'),
                'topics': topics,
                'madhab': None,  # Hadith are pre-madhab
            }

            processed.append(processed_hadith)

        return processed

    except Exception as e:
        print(f"Error processing {file_path}: {e}")
        return []


def process_fatwa_file(file_path: Path) -> List[Dict]:
    """Process a fatwa JSON file"""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            fatawa = json.load(f)

        processed = []
        for fatwa in fatawa:
            # Clean texts
            question = clean_text(fatwa.get('question', ''))
            ruling = clean_text(fatwa.get('ruling', ''))

            if not ruling or len(ruling) < 50:  # Skip very short entries
                continue

            # Process topics
            topics = [normalize_topic(t) for t in fatwa.get('topics', [])]
            if not topics:
                topics = ['general']

            # Extract evidence from ruling if not present
            evidence = fatwa.get('evidence', [])
            if not evidence:
                evidence = extract_evidence_from_text(ruling)

            processed_fatwa = {
                'id': fatwa.get('id', str(uuid.uuid4())),
                'type': 'fatwa',
                'question': question,
                'ruling': ruling,
                'evidence': evidence,
                'source': fatwa.get('source', {}),
                'topics': topics,
                'madhab': fatwa.get('madhab', 'general'),
                'date': fatwa.get('date'),
            }

            processed.append(processed_fatwa)

        return processed

    except Exception as e:
        print(f"Error processing {file_path}: {e}")
        return []


def process_all_data():
    """Process all raw data files"""
    print(f"\n{'='*60}")
    print("Processing Fiqh Data")
    print(f"{'='*60}")

    all_entries = []
    sources_info = {
        'hadith_collections': [],
        'fatwa_sources': [],
        'total_entries': 0,
        'entries_by_type': {},
    }

    # Process hadith files
    hadith_dir = RAW_DATA_DIR / 'hadith'
    if hadith_dir.exists():
        print("\nProcessing hadith collections...")
        # Process JSON files directly in hadith directory
        for json_file in hadith_dir.glob('*.json'):
            print(f"  Processing: {json_file.name}")
            entries = process_hadith_file(json_file)
            all_entries.extend(entries)
            sources_info['hadith_collections'].append({
                'file': json_file.name,
                'count': len(entries)
            })
        # Also check subdirectories
        for collection_dir in hadith_dir.iterdir():
            if collection_dir.is_dir():
                for json_file in collection_dir.glob('*.json'):
                    print(f"  Processing: {json_file.name}")
                    entries = process_hadith_file(json_file)
                    all_entries.extend(entries)
                    sources_info['hadith_collections'].append({
                        'file': json_file.name,
                        'count': len(entries)
                    })

    # Process fatwa files
    fatwa_dir = RAW_DATA_DIR / 'fatawa'
    if fatwa_dir.exists():
        print("\nProcessing fatawa...")
        for json_file in fatwa_dir.glob('*.json'):
            print(f"  Processing: {json_file.name}")
            entries = process_fatwa_file(json_file)
            all_entries.extend(entries)
            sources_info['fatwa_sources'].append({
                'file': json_file.name,
                'count': len(entries)
            })

    # Calculate statistics
    sources_info['total_entries'] = len(all_entries)

    type_counts = {}
    for entry in all_entries:
        entry_type = entry.get('type', 'unknown')
        type_counts[entry_type] = type_counts.get(entry_type, 0) + 1

    sources_info['entries_by_type'] = type_counts

    # Create output directory
    PROCESSED_DATA_DIR.mkdir(parents=True, exist_ok=True)

    # Save processed database
    print(f"\nSaving processed database...")
    with open(OUTPUT_FILE, 'w', encoding='utf-8') as f:
        json.dump(all_entries, f, ensure_ascii=False, indent=2)

    # Save sources info
    with open(SOURCES_FILE, 'w', encoding='utf-8') as f:
        json.dump(sources_info, f, ensure_ascii=False, indent=2)

    print(f"\n{'='*60}")
    print("Processing Complete!")
    print(f"{'='*60}")
    print(f"Total entries processed: {len(all_entries)}")
    print(f"Entries by type:")
    for entry_type, count in type_counts.items():
        print(f"  - {entry_type}: {count}")
    print(f"\nOutput files:")
    print(f"  - Database: {OUTPUT_FILE}")
    print(f"  - Sources: {SOURCES_FILE}")


def main():
    """Main function"""
    process_all_data()


if __name__ == '__main__':
    main()
