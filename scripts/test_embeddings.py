"""
Simple test script to check if embeddings can be generated
"""

import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from sentence_transformers import SentenceTransformer
import json


def test_embeddings():
    """Test if embeddings can be generated"""
    print("Testing embedding generation...")
    
    # Load the RAG data
    rag_data_path = 'rag_data/rag_chunks.json'
    with open(rag_data_path, 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    # Get first chunk for testing
    first_chunk = None
    for category_chunks in data.values():
        if category_chunks:
            first_chunk = category_chunks[0]
            break
    
    if not first_chunk:
        print("No chunks found in data!")
        return
    
    print(f"Using chunk from: {first_chunk['fund_name']}")
    
    # Create text representation
    text_parts = [f"Fund: {first_chunk['fund_name']}"]
    for key, value in first_chunk['data'].items():
        if isinstance(value, dict):
            text_parts.append(f"{key}: {json.dumps(value)}")
        else:
            text_parts.append(f"{key}: {value}")
    chunk_text = " ".join(text_parts)
    
    print(f"Chunk text: {chunk_text[:100]}...")
    
    # Load model and create embedding
    print("Loading model...")
    model = SentenceTransformer('all-MiniLM-L6-v2')
    
    print("Generating embedding...")
    embedding = model.encode([chunk_text])
    
    print(f"Embedding shape: {embedding.shape}")
    print("Test successful!")


if __name__ == "__main__":
    test_embeddings()