#!/usr/bin/env python3
"""
Convert IslamQA dataset to FiqhEntry schema
"""

import json
import csv
import re
from pathlib import Path
from typing import Dict, List
from tqdm import tqdm

# Paths
BASE_DIR = Path(__file__).parent.parent
ISLAMQA_FILE = BASE_DIR / 'temp_islamqa' / 'islamqascprapping.csv'
OUTPUT_DIR = BASE_DIR / 'data' / 'raw' / 'fatawa'


def clean_text(text: str) -> str:
    """Clean and normalize text"""
    if not text:
        return ''

    # Remove extra whitespace
    text = re.sub(r'\s+', ' ', text)
    text = text.strip()

    return text


def extract_topics_from_title(title: str) -> List[str]:
    """Extract topics from fatwa title"""
    if not title:
        return ['general']

    title_lower = title.lower()

    # Topic keywords for fatawa
    topic_keywords = {
        'prayer': ['صلاة', 'صلوات', 'prayer', 'salah', 'صلى'],
        'fasting': ['صيام', 'صوم', 'fasting', 'رمضان', 'ramadan'],
        'zakat': ['زكاة', 'zakat', 'charity'],
        'hajj': ['حج', 'عمرة', 'hajj', 'umrah'],
        'purification': ['طهارة', 'وضوء', 'غسل', 'purification', 'wudu'],
        'marriage': ['زواج', 'نكاح', 'طلاق', 'marriage', 'divorce'],
        'faith': ['إيمان', 'عقيدة', 'faith', 'belief'],
        'quran': ['قرآن', 'quran', 'recitation', 'تلاوة'],
        'hadith': ['حديث', 'hadith', 'سنة'],
        'family': ['أسرة', 'أهل', 'family', 'والدين', 'parents'],
        'business': ['معاملات', 'بيع', 'شراء', 'تجارة', 'business', 'trade'],
        'inheritance': ['ميراث', 'inheritance', 'وراثة'],
        'food': ['طعام', 'أكل', 'food', 'eating'],
        'manners': ['أخلاق', 'آداب', 'manners', 'behavior'],
        'worship': ['عبادة', 'عبادات', 'worship'],
    }

    topics = []
    for topic, keywords in topic_keywords.items():
        if any(keyword in title_lower for keyword in keywords):
            topics.append(topic)

    return topics if topics else ['general']


def extract_evidence(text: str) -> List[str]:
    """Extract Quran verses and hadith references from text"""
    evidence = []

    # Look for Quran verse patterns (Arabic numbering)
    quran_patterns = [
        r'سورة\s+\w+\s*[:：]\s*\d+',
        r'\[[\w\s]+:\s*\d+\]',
    ]

    for pattern in quran_patterns:
        matches = re.findall(pattern, text)
        evidence.extend(matches)

    # Look for hadith references
    hadith_keywords = ['رواه البخاري', 'رواه مسلم', 'متفق عليه', 'صحيح البخاري', 'صحيح مسلم']
    for keyword in hadith_keywords:
        if keyword in text:
            evidence.append(keyword)

    # Remove duplicates
    return list(set(evidence))


def convert_fatwa(row: Dict) -> Dict:
    """Convert a single fatwa to FiqhEntry format"""
    # Get fields
    fatwa_id = row.get('رقم السؤال', '')
    url = row.get('الرابط', '')
    title = clean_text(row.get('العنوان', ''))
    question = clean_text(row.get('السؤال', ''))
    summary = clean_text(row.get('ملخص الإجابة', ''))
    full_answer = clean_text(row.get('الإجابة الكاملة', ''))

    # Use full answer if available, otherwise summary
    ruling = full_answer if full_answer else summary

    # Extract topics
    topics = extract_topics_from_title(title)

    # Extract evidence
    evidence = extract_evidence(ruling)

    # Build FiqhEntry
    entry = {
        'id': f"islamqa_{fatwa_id}",
        'type': 'fatwa',
        'question': question if question else title,
        'ruling': ruling,
        'evidence': evidence,
        'source': {
            'title': 'IslamQA.info',
            'reference': f'Fatwa No. {fatwa_id}',
            'url': url if url else f'https://islamqa.info/ar/answers/{fatwa_id}',
            'scholar': 'IslamQA Scholars'
        },
        'madhab': 'general',  # IslamQA doesn't always specify madhab
        'topics': topics,
        'arabicText': ruling,  # The text is in Arabic
    }

    return entry


def main():
    """Main conversion function"""
    print("="*60)
    print("IslamQA Dataset Converter")
    print("Converting IslamQA fatawa to FiqhEntry schema")
    print("="*60)

    if not ISLAMQA_FILE.exists():
        print(f"Error: IslamQA CSV file not found at {ISLAMQA_FILE}")
        return

    # Create output directory
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    # Read CSV
    print(f"\nReading {ISLAMQA_FILE}...")
    fatawa = []

    with open(ISLAMQA_FILE, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        rows = list(reader)

    print(f"Found {len(rows)} fatawa")

    # Convert each fatwa
    entries = []
    for row in tqdm(rows, desc="Converting fatawa"):
        try:
            entry = convert_fatwa(row)
            if entry['ruling']:  # Only include if we have a ruling
                entries.append(entry)
        except Exception as e:
            print(f"\nError converting fatwa {row.get('رقم السؤال')}: {e}")
            continue

    # Save output
    output_file = OUTPUT_DIR / 'islamqa_fatawa.json'
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(entries, f, ensure_ascii=False, indent=2)

    print("\n" + "="*60)
    print("Conversion Complete!")
    print("="*60)
    print(f"Total fatawa converted: {len(entries)}")
    print(f"Output file: {output_file}")
    print(f"File size: {output_file.stat().st_size / (1024*1024):.1f} MB")

    # Print topic statistics
    print("\nTop topics:")
    topic_counts = {}
    for entry in entries:
        for topic in entry['topics']:
            topic_counts[topic] = topic_counts.get(topic, 0) + 1

    for topic, count in sorted(topic_counts.items(), key=lambda x: x[1], reverse=True)[:10]:
        print(f"  {topic}: {count}")


if __name__ == '__main__':
    main()
