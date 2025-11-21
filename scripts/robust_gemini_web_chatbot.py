"""
Web Interface for Robust Gemini-Enhanced FAQ Assistant
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

# Try to import Google Generative AI with better error handling
GOOGLE_AI_AVAILABLE = False
genai = None

try:
    import google.generativeai as genai_module
    genai = genai_module
    GOOGLE_AI_AVAILABLE = True
except ImportError:
    print("Google Generative AI library not found.")
except Exception as e:
    print(f"Google Generative AI library error: {e}")

from sentence_transformers import SentenceTransformer
from sklearn.metrics.pairwise import cosine_similarity
from flask import Flask, render_template, request, jsonify

app = Flask(__name__)

class WebRobustGeminiFAQAssistant:
    def __init__(self, rag_data_path='rag_data/rag_chunks.json', embeddings_path='rag_data/embeddings.pkl', api_key=None):
        """Initialize web FAQ assistant with RAG data and robust Gemini integration"""
        self.model = SentenceTransformer('all-MiniLM-L6-v2')
        self.rag_data_path = rag_data_path
        self.embeddings_path = embeddings_path
        self.chunks = []
        self.embeddings = []
        self.conversation_history = []
        self.session_start = datetime.now()
        
        # Get API key from parameter, environment variable, or None
        self.api_key = api_key or os.environ.get('GOOGLE_API_KEY')
        
        # Google Generative AI setup with better error handling
        self.gemini_model = None
        if GOOGLE_AI_AVAILABLE and self.api_key:
            try:
                genai.configure(api_key=self.api_key)
                # Try different models in order of preference
                models_to_try = ['gemini-1.5-flash-latest', 'gemini-pro', 'gemini-1.5-pro-latest']
                for model_name in models_to_try:
                    try:
                        self.gemini_model = genai.GenerativeModel(model_name)
                        print(f"Gemini integration enabled with {model_name} model")
                        break
                    except Exception as e:
                        print(f"Failed to initialize {model_name}: {e}")
                        continue
                
                if not self.gemini_model:
                    print("Could not initialize any Gemini model")
            except Exception as e:
                print(f"Error configuring Gemini: {e}")
        elif GOOGLE_AI_AVAILABLE and not self.api_key:
            print("Google Generative AI library available but no API key provided")
        else:
            print("Google Generative AI library not available")
        
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
        try:
            with open(self.embeddings_path, 'rb') as f:
                self.embeddings = pickle.load(f)
            print("Embeddings loaded successfully")
        except Exception as e:
            print(f"Error loading embeddings: {e}")
            print("Creating new embeddings...")
            self.create_embeddings()
    
    def create_embeddings(self):
        """Create embeddings for all chunks"""
        print("Creating embeddings for all chunks...")
        texts = []
        for chunk in self.chunks:
            # Create a text representation of the chunk
            text_parts = [f"Fund: {chunk['fund_name']}"]
            text_parts.append(f"Category: {chunk['chunk_type']}")
            for key, value in chunk['data'].items():
                if isinstance(value, dict):
                    for sub_key, sub_value in value.items():
                        text_parts.append(f"{key} {sub_key}: {sub_value}")
                else:
                    text_parts.append(f"{key}: {value}")
            texts.append(" ".join(text_parts))
        
        # Create embeddings
        self.embeddings = self.model.encode(texts)
        print("Embeddings created successfully")
    
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
    
    def format_context_for_llm(self, relevant_chunks: List[Dict]) -> str:
        """Format context for LLM prompt"""
        if not relevant_chunks:
            return "No relevant information found."
        
        context_parts = []
        context_parts.append("Relevant information about UTI mutual funds:")
        
        for i, result in enumerate(relevant_chunks, 1):
            chunk = result['chunk']
            context_parts.append(f"\n{i}. Fund: {chunk['fund_name']}")
            context_parts.append(f"   Category: {chunk['chunk_type'].replace('_', ' ').title()}")
            
            # Add the data
            for key, value in chunk['data'].items():
                formatted_key = key.replace('_', ' ').title()
                if isinstance(value, dict):
                    context_parts.append(f"   {formatted_key}:")
                    for sub_key, sub_value in value.items():
                        context_parts.append(f"     {sub_key.title()}: {sub_value}")
                else:
                    context_parts.append(f"   {formatted_key}: {value}")
            
            # Add source
            context_parts.append(f"   Source: {chunk['source_url']}")
        
        return "\n".join(context_parts)
    
    def generate_gemini_response(self, question: str, context: str) -> str:
        """Generate response using Gemini"""
        if not self.gemini_model:
            # Fallback to basic response generation
            return self.generate_basic_response(question, context)
        
        try:
            # Create prompt for Gemini
            prompt = f"""
You are a helpful assistant answering questions about UTI mutual funds. 
Use the following context to answer the question accurately and concisely.

Context:
{context}

Question: {question}

Please provide a helpful, conversational response based on the context above. 
If the context doesn't contain relevant information, politely say so.
Format your response in a clear, easy-to-read manner.
This is for factual information only. Do not provide investment advice.

Response:
"""

            # Call Gemini API with timeout
            try:
                # Try async version first
                response = self.gemini_model.generate_content(prompt, timeout=30)
            except:
                # Fallback to sync version
                response = self.gemini_model.generate_content(prompt)
            
            return response.text.strip()
            
        except Exception as e:
            print(f"Error calling Gemini API: {e}")
            # Fallback to basic response
            return self.generate_basic_response(question, context)
    
    def generate_basic_response(self, question: str, context: str) -> str:
        """Generate basic response when LLM is not available"""
        # Extract key information from context
        lines = context.split('\n')
        if len(lines) > 10:
            # Truncate for readability
            context_summary = '\n'.join(lines[:10]) + "\n... (more information available)"
        else:
            context_summary = context
        
        return f"""Based on the information I found:

{context_summary}"""
    
    def answer_question(self, question: str) -> Dict:
        """Generate answer for a question using relevant chunks"""
        # Find relevant chunks
        relevant_chunks = self.find_relevant_chunks(question)
        
        # Format context
        context = self.format_context_for_llm(relevant_chunks)
        
        # Generate response
        if self.gemini_model and self.api_key:
            response_text = self.generate_gemini_response(question, context)
        else:
            response_text = self.generate_basic_response(question, context)
        
        # Format sources
        sources = []
        for result in relevant_chunks:
            chunk = result['chunk']
            sources.append({
                "fund_name": chunk['fund_name'],
                "url": chunk['source_url'],
                "type": chunk['chunk_type']
            })
        
        # Add to conversation history
        self.conversation_history.append({
            'timestamp': datetime.now().isoformat(),
            'question': question,
            'response': response_text,
            'chunks_found': len(relevant_chunks),
            'used_llm': bool(self.gemini_model and self.api_key)
        })
        
        return {
            "response": response_text,
            "sources": sources
        }

# Initialize the assistant (will get API key from environment in the route)
assistant = None

@app.route('/')
def index():
    return render_template('simple_ui.html')

@app.route('/init', methods=['POST'])
def initialize_assistant():
    global assistant
    try:
        # Get JSON data from request
        data = request.get_json()
        
        # Check if data is valid
        if data is None:
            return jsonify({'status': 'error', 'message': 'Invalid JSON data'}), 400
            
        api_key = data.get('api_key', '').strip()
        
        # If no API key provided in request, try to get from environment
        if not api_key:
            import os
            api_key = os.environ.get('GOOGLE_API_KEY', '')
        
        # Initialize assistant with provided API key
        assistant = WebRobustGeminiFAQAssistant(api_key=api_key)
        return jsonify({'status': 'success', 'message': 'Assistant initialized successfully'})
    except Exception as e:
        import traceback
        traceback.print_exc()
        return jsonify({'status': 'error', 'message': str(e)}), 500

@app.route('/ask', methods=['POST'])
def ask_question():
    global assistant
    try:
        if not assistant:
            return jsonify({'error': 'Assistant not initialized. Please provide API key first.'}), 400
            
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
    global assistant
    if not assistant:
        return jsonify([])
    return jsonify(assistant.conversation_history)

if __name__ == '__main__':
    print("Starting Web Robust Gemini FAQ Assistant...")
    print("Open your browser to http://localhost:5000")
    app.run(debug=True, host='0.0.0.0', port=5000)