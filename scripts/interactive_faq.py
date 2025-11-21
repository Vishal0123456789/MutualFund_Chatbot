"""
Enhanced Interactive FAQ Assistant with Chatbot Capabilities
"""

import sys
import json
import pickle
import numpy as np
from pathlib import Path
from datetime import datetime
from typing import List, Dict, Any

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from sentence_transformers import SentenceTransformer
from sklearn.metrics.pairwise import cosine_similarity


class EnhancedFAQAssistant:
    def __init__(self, rag_data_path='rag_data/rag_chunks.json', embeddings_path='rag_data/embeddings.pkl'):
        """Initialize enhanced FAQ assistant with RAG data"""
        self.model = SentenceTransformer('all-MiniLM-L6-v2')
        self.rag_data_path = rag_data_path
        self.embeddings_path = embeddings_path
        self.chunks = []
        self.embeddings = []
        self.conversation_history = []
        self.session_start = datetime.now()
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
        
        # Load embeddings from disk
        print("Loading embeddings from disk...")
        with open(self.embeddings_path, 'rb') as f:
            self.embeddings = pickle.load(f)
        print("Embeddings loaded successfully")
    
    def find_relevant_chunks(self, question: str, top_k: int = 3) -> List[Dict]:
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
    
    def format_chunk_data(self, chunk_data: Dict) -> str:
        """Format chunk data in a readable way"""
        formatted_parts = []
        for key, value in chunk_data.items():
            # Format key to be more readable
            formatted_key = key.replace('_', ' ').title()
            
            # Handle different data types
            if isinstance(value, dict):
                formatted_parts.append(f"{formatted_key}:")
                for sub_key, sub_value in value.items():
                    formatted_parts.append(f"  • {sub_key.title()}: {sub_value}")
            else:
                formatted_parts.append(f"{formatted_key}: {value}")
        
        return "\n".join(formatted_parts)
    
    def generate_conversational_response(self, question: str, relevant_chunks: List[Dict]) -> str:
        """Generate a conversational response using relevant chunks"""
        if not relevant_chunks:
            return "I couldn't find relevant information to answer your question. Could you please rephrase or ask about a different topic?"
        
        # Create a more natural response
        response_parts = []
        
        # Add an introductory phrase
        if len(relevant_chunks) == 1:
            response_parts.append("I found this information that might help:")
        else:
            response_parts.append("I found some information that might help:")
        
        # Add information from relevant chunks
        for i, result in enumerate(relevant_chunks, 1):
            chunk = result['chunk']
            similarity = result['similarity']
            
            # Add fund name and type
            response_parts.append(f"\n{i}. {chunk['fund_name']} ({chunk['chunk_type'].replace('_', ' ').title()})")
            
            # Add the formatted data
            formatted_data = self.format_chunk_data(chunk['data'])
            response_parts.append(formatted_data)
            
            # Add source attribution
            response_parts.append(f"Source: {chunk['source_url']}")
        
        # Add a closing phrase
        response_parts.append("\nIs there anything specific about this information you'd like to know more about?")
        
        return "\n".join(response_parts)
    
    def get_conversation_context(self) -> str:
        """Get conversation context for better responses"""
        if not self.conversation_history:
            return ""
        
        context_parts = []
        # Include last 3 interactions for context
        for interaction in self.conversation_history[-3:]:
            context_parts.append(f"Q: {interaction['question']}")
            context_parts.append(f"A: {interaction['response'][:100]}...")  # Limit length
        
        return "\n".join(context_parts)
    
    def answer_question(self, question: str) -> str:
        """Generate answer for a question using relevant chunks"""
        print(f"\nQuestion: {question}")
        
        # Find relevant chunks
        relevant_chunks = self.find_relevant_chunks(question)
        
        # Generate conversational response
        response = self.generate_conversational_response(question, relevant_chunks)
        
        # Add to conversation history
        self.conversation_history.append({
            'timestamp': datetime.now().isoformat(),
            'question': question,
            'response': response,
            'chunks_found': len(relevant_chunks)
        })
        
        return response
    
    def get_session_summary(self) -> str:
        """Get summary of current session"""
        duration = datetime.now() - self.session_start
        minutes = duration.total_seconds() / 60
        
        return f"""
Session Summary:
- Duration: {minutes:.1f} minutes
- Questions asked: {len(self.conversation_history)}
- Session started: {self.session_start.strftime('%Y-%m-%d %H:%M:%S')}
        """


def main():
    """Main function to run enhanced interactive FAQ assistant"""
    print("Starting Enhanced Interactive FAQ Assistant...")
    print("Loading data and embeddings...")
    
    # Initialize assistant
    assistant = EnhancedFAQAssistant()
    
    print("\n" + "="*80)
    print("Enhanced Interactive FAQ Assistant Ready!")
    print("="*80)
    print("Ask questions about UTI mutual funds, or type 'quit' to exit.")
    print("Type 'summary' to see session statistics.")
    print("\nExample questions:")
    print("  - What is the expense ratio of UTI ELSS Tax Saver Fund?")
    print("  - What is the risk level of UTI Small Cap Fund?")
    print("  - How can I download my transaction history from Groww?")
    print("  - What is the benchmark for UTI Nifty 50 Index Fund?")
    print("="*80)
    
    while True:
        try:
            question = input("\nYou: ").strip()
            
            if question.lower() in ['quit', 'exit', 'q']:
                print("\nAssistant: Thank you for using the FAQ assistant! Here's your session summary:")
                print(assistant.get_session_summary())
                print("Goodbye!")
                break
            
            if question.lower() == 'summary':
                print("\nAssistant:", assistant.get_session_summary())
                continue
            
            if not question:
                continue
                
            answer = assistant.answer_question(question)
            print(f"\nAssistant:\n{answer}")
            
        except KeyboardInterrupt:
            print("\n\nAssistant: Thank you for using the FAQ assistant! Here's your session summary:")
            print(assistant.get_session_summary())
            print("Goodbye!")
            break
        except Exception as e:
            print(f"Error: {e}")


if __name__ == "__main__":
    main()