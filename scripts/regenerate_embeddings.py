"""
Regenerate embeddings for RAG chunks after data updates
"""
import json
import pickle
import numpy as np
from pathlib import Path
from datetime import datetime
from sentence_transformers import SentenceTransformer

# Paths
rag_data_path = Path(__file__).parent.parent / 'rag_data' / 'rag_chunks.json'
embeddings_path = Path(__file__).parent.parent / 'rag_data' / 'embeddings.pkl'

print("Loading RAG data...")
with open(rag_data_path, 'r', encoding='utf-8') as f:
    data = json.load(f)

# Flatten all chunks
chunks = []
for category_chunks in data.values():
    chunks.extend(category_chunks)

print(f"Loaded {len(chunks)} chunks")

# Initialize model
print("Loading sentence-transformers model...")
model = SentenceTransformer('all-MiniLM-L6-v2')

# Create text representations of chunks for embedding
chunk_texts = []
for chunk in chunks:
    # Create a text representation of the chunk with fund name repeated for importance
    fund_name = chunk.get('fund_name', '')
    chunk_type = chunk.get('chunk_type', '')
    data_str = ' '.join(f"{k}: {v}" for k, v in chunk.get('data', {}).items())
    
    # Repeat fund name to give it more weight in embedding
    chunk_text = f"{fund_name} {fund_name} {chunk_type} {data_str}"
    chunk_texts.append(chunk_text)

print(f"Creating embeddings for {len(chunk_texts)} chunks...")
embeddings = model.encode(chunk_texts)

print(f"Embeddings shape: {embeddings.shape}")

# Save embeddings with metadata to force version change
print(f"Saving embeddings to {embeddings_path}...")
with open(embeddings_path, 'wb') as f:
    # Store embeddings with metadata
    data_to_save = {
        'embeddings': embeddings,
        'metadata': {
            'version': '2.0',
            'chunks_count': len(chunks),
            'model': 'all-MiniLM-L6-v2',
            'timestamp': datetime.now().isoformat()
        }
    }
    pickle.dump(data_to_save, f)

print("✅ Embeddings regenerated successfully!")
print(f"Total chunks: {len(chunks)}")
print(f"Embeddings saved: {embeddings_path}")
