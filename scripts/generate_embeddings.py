#!/usr/bin/env python3
"""
Script to generate embeddings for fiqh entries and store in ChromaDB
"""

import json
import os
from pathlib import Path
from typing import List, Dict, Any
from tqdm import tqdm
import chromadb
from chromadb.config import Settings
from openai import OpenAI
from dotenv import load_dotenv
import time

# Load environment variables
load_dotenv()

# Paths
DATA_DIR = Path(__file__).parent.parent / 'data'
PROCESSED_DATA_FILE = DATA_DIR / 'processed' / 'fiqh_database.json'
CHROMA_DIR = DATA_DIR / 'embeddings' / 'chroma_db'

# Configuration
EMBEDDING_MODEL = os.getenv('EMBEDDING_MODEL', 'text-embedding-3-small')
CHROMA_COLLECTION = os.getenv('CHROMA_COLLECTION', 'fiqh_embeddings')
BATCH_SIZE = 100  # Process embeddings in batches


def load_fiqh_database() -> List[Dict]:
    """Load the processed fiqh database"""
    print(f"Loading fiqh database from {PROCESSED_DATA_FILE}")

    if not PROCESSED_DATA_FILE.exists():
        raise FileNotFoundError(
            f"Processed database not found at {PROCESSED_DATA_FILE}\n"
            "Please run process_texts.py first to create the database."
        )

    with open(PROCESSED_DATA_FILE, 'r', encoding='utf-8') as f:
        data = json.load(f)

    print(f"Loaded {len(data)} entries")
    return data


def create_embedding_text(entry: Dict) -> str:
    """Create a combined text for embedding"""
    parts = []

    # Add question for fatawa
    if entry.get('question'):
        parts.append(f"Question: {entry['question']}")

    # Add the ruling/content
    parts.append(entry.get('ruling', ''))

    # Add evidence
    evidence = entry.get('evidence', [])
    if evidence:
        parts.append(f"Evidence: {' | '.join(evidence)}")

    # Add topics for context
    topics = entry.get('topics', [])
    if topics:
        parts.append(f"Topics: {', '.join(topics)}")

    # Add madhab for context
    madhab = entry.get('madhab')
    if madhab and madhab != 'general':
        parts.append(f"Madhab: {madhab}")

    return '\n\n'.join(parts)


def generate_embeddings_openai(texts: List[str], client: OpenAI) -> List[List[float]]:
    """Generate embeddings using OpenAI API"""
    try:
        response = client.embeddings.create(
            model=EMBEDDING_MODEL,
            input=texts
        )

        embeddings = [item.embedding for item in response.data]
        return embeddings

    except Exception as e:
        print(f"Error generating embeddings: {e}")
        raise


def setup_chromadb() -> tuple:
    """Set up ChromaDB client and collection"""
    print(f"\nSetting up ChromaDB...")
    print(f"Storage directory: {CHROMA_DIR}")

    # Create directory
    CHROMA_DIR.mkdir(parents=True, exist_ok=True)

    # Create client
    client = chromadb.PersistentClient(
        path=str(CHROMA_DIR),
        settings=Settings(anonymized_telemetry=False)
    )

    # Get or create collection
    try:
        # Try to get existing collection
        collection = client.get_collection(name=CHROMA_COLLECTION)
        print(f"Found existing collection '{CHROMA_COLLECTION}' with {collection.count()} entries")

        # Ask user if they want to reset
        response = input("Do you want to reset the collection? (y/N): ")
        if response.lower() == 'y':
            client.delete_collection(name=CHROMA_COLLECTION)
            collection = client.create_collection(name=CHROMA_COLLECTION)
            print("Collection reset")
        else:
            print("Using existing collection")

    except Exception:
        # Collection doesn't exist, create it
        collection = client.create_collection(name=CHROMA_COLLECTION)
        print(f"Created new collection '{CHROMA_COLLECTION}'")

    return client, collection


def add_to_chromadb(
    collection,
    entries: List[Dict],
    embeddings: List[List[float]],
):
    """Add entries and embeddings to ChromaDB"""
    ids = [entry['id'] for entry in entries]
    documents = [entry.get('ruling', '')[:1000] for entry in entries]  # Store truncated text

    # Prepare metadata (ChromaDB has limitations on metadata)
    metadatas = []
    for entry in entries:
        metadata = {
            'type': entry.get('type', 'unknown'),
            'source_title': entry.get('source', {}).get('title', ''),
            'source_ref': entry.get('source', {}).get('reference', ''),
            'topics': ','.join(entry.get('topics', [])),
        }

        # Add optional fields
        if entry.get('madhab'):
            metadata['madhab'] = entry['madhab']

        if entry.get('authenticity'):
            metadata['authenticity'] = entry['authenticity']

        if entry.get('question'):
            metadata['question'] = entry['question'][:200]  # Truncate

        metadatas.append(metadata)

    # Add to collection
    collection.add(
        ids=ids,
        embeddings=embeddings,
        documents=documents,
        metadatas=metadatas
    )


def main():
    """Main function to generate embeddings"""
    print(f"\n{'='*60}")
    print("Fiqh Embeddings Generator")
    print(f"{'='*60}")

    # Check for OpenAI API key
    openai_key = os.getenv('OPENAI_API_KEY')
    if not openai_key:
        raise ValueError(
            "OPENAI_API_KEY not found in environment.\n"
            "Please set it in your .env file or environment variables."
        )

    # Initialize OpenAI client
    client = OpenAI(api_key=openai_key)
    print(f"Using embedding model: {EMBEDDING_MODEL}")

    # Load database
    entries = load_fiqh_database()

    # Set up ChromaDB
    chroma_client, collection = setup_chromadb()

    # Get existing IDs to skip already embedded entries
    existing_ids = set()
    try:
        existing = collection.get()
        existing_ids = set(existing['ids'])
        print(f"Found {len(existing_ids)} existing embeddings")
    except Exception:
        pass

    # Filter entries to process
    entries_to_process = [e for e in entries if e['id'] not in existing_ids]

    if not entries_to_process:
        print("\nAll entries already have embeddings. Nothing to do!")
        return

    print(f"\nGenerating embeddings for {len(entries_to_process)} entries...")
    print(f"Processing in batches of {BATCH_SIZE}")

    # Process in batches
    for i in tqdm(range(0, len(entries_to_process), BATCH_SIZE), desc="Batches"):
        batch = entries_to_process[i:i + BATCH_SIZE]

        # Create embedding texts
        texts = [create_embedding_text(entry) for entry in batch]

        # Generate embeddings
        try:
            embeddings = generate_embeddings_openai(texts, client)

            # Add to ChromaDB
            add_to_chromadb(collection, batch, embeddings)

            # Rate limiting
            time.sleep(0.5)

        except Exception as e:
            print(f"\nError processing batch {i//BATCH_SIZE + 1}: {e}")
            print("Stopping to avoid data loss. You can re-run to continue from this point.")
            break

    # Print summary
    final_count = collection.count()
    print(f"\n{'='*60}")
    print("Embedding generation complete!")
    print(f"{'='*60}")
    print(f"Total embeddings in database: {final_count}")
    print(f"ChromaDB location: {CHROMA_DIR}")
    print(f"Collection name: {CHROMA_COLLECTION}")


if __name__ == '__main__':
    main()
