"""
FAQ assistant with embedding saving capability
"""

import sys
import json
import pickle
import numpy as np
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from sentence_transformers import SentenceTransformer
from sklearn.metrics.pairwise import cosine_similarity


class FAQAssistant:
    def __init__(self, rag_data_path='rag_data/rag_chunks.json', embeddings_path='rag_data/embeddings.pkl'):
        """Initialize FAQ assistant with RAG data"""
        self.model = SentenceTransformer('all-MiniLM-L6-v2')
        self.rag_data_path = rag_data_path
        self.embeddings_path = embeddings_path
        self.chunks = []
        self.embeddings = []
        self.load_and_prepare_data()
    
    def load_and_prepare_data(self):
        """Load RAG data and prepare embeddings"""
        print("Loading RAG data...")
        
        # Load chunks from JSON
        with open(self.rag_data_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        # Flatten all chunks into a single list
        for category_chunks in data.values():
            self.chunks.extend(category_chunks)
        
        print(f"Loaded {len(self.chunks)} chunks")
        
        # Try to load embeddings from disk
        if Path(self.embeddings_path).exists():
            print("Loading embeddings from disk...")
            with open(self.embeddings_path, 'rb') as f:
                self.embeddings = pickle.load(f)
            print("Embeddings loaded successfully")
        else:
            # Create embeddings for all chunks
            print("Creating embeddings...")
            chunk_texts = []
            for chunk in self.chunks:
                # Create a text representation of the chunk for embedding
                text_parts = [f"Fund: {chunk['fund_name']}"]
                for key, value in chunk['data'].items():
                    if isinstance(value, dict):
                        text_parts.append(f"{key}: {json.dumps(value)}")
                    else:
                        text_parts.append(f"{key}: {value}")
                chunk_texts.append(" ".join(text_parts))
            
            self.embeddings = self.model.encode(chunk_texts)
            print("Embeddings created successfully")
            
            # Save embeddings to disk
            print("Saving embeddings to disk...")
            with open(self.embeddings_path, 'wb') as f:
                pickle.dump(self.embeddings, f)
            print("Embeddings saved successfully")
    
    def find_relevant_chunks(self, question, top_k=3):
        """Find most relevant chunks for a given question"""
        # Create embedding for the question
        question_embedding = self.model.encode([question])
        
        # Calculate similarities
        similarities = cosine_similarity(question_embedding, self.embeddings)[0]
        
        # Get top-k most similar chunks
        top_indices = np.argsort(similarities)[-top_k:][::-1]
        
        results = []
        for idx in top_indices:
            if similarities[idx] > 0.1:  # Threshold to filter out irrelevant chunks
                results.append({
                    'chunk': self.chunks[idx],
                    'similarity': similarities[idx]
                })
        
        return results
    
    def answer_question(self, question):
        """Generate answer for a question using relevant chunks"""
        print(f"\nQuestion: {question}")
        
        # Find relevant chunks
        relevant_chunks = self.find_relevant_chunks(question)
        
        if not relevant_chunks:
            return "I couldn't find relevant information to answer your question."
        
        print(f"\nFound {len(relevant_chunks)} relevant chunks:")
        
        # Display relevant chunks
        answer_parts = []
        for i, result in enumerate(relevant_chunks, 1):
            chunk = result['chunk']
            similarity = result['similarity']
            print(f"\n{i}. {chunk['fund_name']} (Similarity: {similarity:.3f})")
            print(f"   Source: {chunk['source_url']}")
            print(f"   Type: {chunk['chunk_type']}")
            print("   Data:")
            for key, value in chunk['data'].items():
                print(f"     {key}: {value}")
            
            # Add to answer
            answer_parts.append(f"From {chunk['fund_name']} ({chunk['chunk_type']}):")
            for key, value in chunk['data'].items():
                answer_parts.append(f"- {key}: {value}")
        
        return "\n\n".join(answer_parts)


def main():
    """Main function to demonstrate FAQ assistant"""
    # Initialize assistant
    assistant = FAQAssistant()
    
    # Example questions
    questions = [
        "What is the expense ratio of UTI ELSS Tax Saver Fund?",
        "What is the risk level of UTI Small Cap Fund?",
        "How can I download my transaction history from Groww?",
        "What is the benchmark for UTI Nifty 50 Index Fund?"
    ]
    
    # Answer each question
    for question in questions:
        answer = assistant.answer_question(question)
        print(f"\nAnswer:\n{answer}")
        print("\n" + "="*80)


if __name__ == "__main__":
    main()