import pickle
import json
from sentence_transformers import SentenceTransformer

print("Loading model...")
model = SentenceTransformer('all-MiniLM-L6-v2')

print("Loading chunks...")
with open('rag_data/rag_chunks.json', 'r', encoding='utf-8') as f:
    data = json.load(f)

chunks = []
for category_chunks in data.values():
    chunks.extend(category_chunks)

print(f"Loaded {len(chunks)} chunks")

print("Generating embeddings...")
texts = []
for chunk in chunks:
    text = f"{chunk['fund_name']} {chunk['chunk_type']} {str(chunk['data'])}"
    texts.append(text)

embeddings = model.encode(texts)

print("Saving embeddings...")
with open('rag_data/embeddings.pkl', 'wb') as f:
    pickle.dump(embeddings, f)

print("Embeddings regenerated successfully!")
print(f"Shape: {embeddings.shape}")
