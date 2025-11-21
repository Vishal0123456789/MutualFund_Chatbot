"""
Web Interface for Enhanced FAQ Assistant
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
from flask import Flask, render_template, request, jsonify

app = Flask(__name__)

class WebFAQAssistant:
    def __init__(self, rag_data_path='rag_data/rag_chunks.json', embeddings_path='rag_data/embeddings.pkl'):
        """Initialize web FAQ assistant with RAG data"""
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
    
    def generate_conversational_response(self, question: str, relevant_chunks: List[Dict]) -> Dict:
        """Generate a conversational response using relevant chunks"""
        if not relevant_chunks:
            return {
                "response": "I couldn't find relevant information to answer your question. Could you please rephrase or ask about a different topic?",
                "sources": []
            }
        
        # Create a more natural response
        response_parts = []
        sources = []
        
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
            source_info = {
                "fund_name": chunk['fund_name'],
                "url": chunk['source_url'],
                "type": chunk['chunk_type']
            }
            sources.append(source_info)
        
        return {
            "response": "\n".join(response_parts),
            "sources": sources
        }
    
    def answer_question(self, question: str) -> Dict:
        """Generate answer for a question using relevant chunks"""
        # Find relevant chunks
        relevant_chunks = self.find_relevant_chunks(question)
        
        # Generate conversational response
        response_data = self.generate_conversational_response(question, relevant_chunks)
        
        # Add to conversation history
        self.conversation_history.append({
            'timestamp': datetime.now().isoformat(),
            'question': question,
            'response': response_data['response'],
            'chunks_found': len(relevant_chunks)
        })
        
        return response_data

# Initialize the assistant
assistant = WebFAQAssistant()

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/ask', methods=['POST'])
def ask_question():
    try:
        data = request.get_json()
        question = data.get('question', '').strip()
        
        if not question:
            return jsonify({'error': 'No question provided'}), 400
        
        response_data = assistant.answer_question(question)
        return jsonify(response_data)
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/history')
def get_history():
    return jsonify(assistant.conversation_history)

if __name__ == '__main__':
    print("Starting Web FAQ Assistant...")
    print("Open your browser to http://localhost:5000")
    app.run(debug=True, host='0.0.0.0', port=5000)