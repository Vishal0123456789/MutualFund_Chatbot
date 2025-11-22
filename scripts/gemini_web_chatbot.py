"""
Web Interface for Gemini-Enhanced FAQ Assistant
"""

import sys
import json
import pickle
import numpy as np
from pathlib import Path
from datetime import datetime
from typing import List, Dict, Any
import subprocess
import os
import requests

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

# Google Generative AI library disabled for web (Python 3.14 compatibility)
GOOGLE_AI_AVAILABLE = False

# Try to load environment variables from .env file
try:
    from load_env import load_env_file
    load_env_file()
except ImportError:
    pass

from sentence_transformers import SentenceTransformer
from sklearn.metrics.pairwise import cosine_similarity
from flask import Flask, render_template, request, jsonify
from flask_cors import CORS

app = Flask(__name__, template_folder=str(Path(__file__).parent.parent / 'templates'))
CORS(app)  # Enable CORS for all routes

class WebGeminiFAQAssistant:
    def __init__(self, rag_data_path='rag_data/rag_chunks.json', embeddings_path='rag_data/embeddings.pkl', api_key=None):
        """Initialize web FAQ assistant with RAG data and Gemini integration"""
        self.model = SentenceTransformer('all-MiniLM-L6-v2')
        self.rag_data_path = rag_data_path
        self.embeddings_path = embeddings_path
        self.chunks = []
        self.embeddings = []
        self.conversation_history = []
        self.session_start = datetime.now()
        
        # Get API key from parameter, environment variable, or None
        self.api_key = api_key or os.environ.get('GOOGLE_API_KEY')
        
        # Google Generative AI setup (REST-only for web)
        self.gemini_model = None
        if self.api_key:
            print("Gemini REST integration enabled")
        else:
            print("Google API key not found - using basic responses")
        
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
    
    def find_relevant_chunks(self, question: str, top_k: int = 10) -> List[Dict]:
        """Find most relevant chunks for a given question"""
        # Create embedding for the question
        question_embedding = self.model.encode([question])
        
        # Calculate similarities
        similarities = cosine_similarity(question_embedding, self.embeddings)[0]
        
        # Get top-k most similar chunks
        top_indices = np.argsort(similarities)[-top_k:][::-1]
        
        results = []
        for idx in top_indices:
            # Lower threshold to 0.2 to catch all relevant chunks
            if similarities[idx] > 0.2:
                results.append({
                    'chunk': self.chunks[idx],
                    'similarity': similarities[idx]
                })
        
        return results
    
    def format_context_for_gemini(self, relevant_chunks: List[Dict]) -> str:
        """Format context for Gemini prompt"""
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
        if not self.api_key:
            # Fallback to basic response generation
            return self.generate_basic_response(question, context)
        
        try:
            # Detect if this is a NAV question for special handling
            q_lower = question.lower()
            is_nav_question = any(k in q_lower for k in ['nav', 'net asset value', 'current price'])
            
            # Create prompt for Gemini with NAV priority
            if is_nav_question:
                prompt = f"""Extract the NAV (Net Asset Value) information from the context.
Provide a direct, concise answer in this format:
"The NAV of [Fund Name] is Rs [NAV amount] as on [date]."

Context:
{context}

Question: {question}

Response:"""
            else:
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

            # Using REST API for Gemini calls
            url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent?key={self.api_key}"
            
            headers = {
                "Content-Type": "application/json"
            }
            
            data = {
                "contents": [{
                    "parts": [{
                        "text": prompt
                    }]
                }]
            }
            
            response = requests.post(url, headers=headers, json=data)
            response.raise_for_status()
            
            result = response.json()
            return result["candidates"][0]["content"]["parts"][0]["text"]
                
        except Exception as e:
            print(f"Error calling Gemini API: {e}")
            # Fallback to basic response
            return self.generate_basic_response(question, context)
    
    def generate_basic_response(self, question: str, context: str) -> str:
        """Generate basic response when LLM is not available"""
        # Return full context without truncation
        return f"""Based on the information I found:

{context}"""
    
    def answer_question(self, question: str) -> Dict:
        """Generate answer for a question using relevant chunks"""
        q = question.lower().strip()
        
        # Detect greeting messages
        greeting_keywords = ['hi', 'hello', 'hey', 'greetings', 'good morning', 'good afternoon', 
                            'good evening', 'what\'s up', 'howdy', 'namaste']
        if any(q == k or q.startswith(k + ' ') for k in greeting_keywords):
            response_text = (
                "Hello! 👋 I'm your UTI Mutual Fund Assistant. I can help you explore and learn more about "
                "UTI's mutual fund offerings. Feel free to ask me about fund details, performance metrics, "
                "expenses, risk information, and more. Or visit Groww to explore all available funds: "
                "https://groww.in/mutual-funds/amc/uti-mutual-funds"
            )
            return {
                "response": response_text,
                "sources": [{"url": "https://groww.in/mutual-funds/amc/uti-mutual-funds", 
                             "fund_name": "Groww - UTI Mutual Funds",
                             "type": "reference"}]
            }
        
        # Guardrail: block investment advice and ranking queries
        advice_keywords = [
            "invest", "buy", "sell", "hold", "recommend", "recommendation",
            "suggest", "allocate", "allocation", "portfolio", "best fund",
            "should i", "advice", "top", "best", "rank", "ranking",
            "outperform", "better than", "worse than", "compare", "comparison"
        ]
        if any(k in q for k in advice_keywords):
            response_text = (
                "This assistant is designed to provide factual information about UTI Mutual Funds only. "
                "It does not provide investment advice."
            )
            return {
                "response": response_text,
                "sources": []
            }
        
        # Detect if user specifies a number of results
        import re
        number_match = re.search(r'(\d+)\s+fund', q)
        top_k = int(number_match.group(1)) if number_match else 10
        top_k = min(top_k, 15)  # Cap at 15 to avoid overwhelming responses
        
        # Determine if question is about NAV - more robust detection
        nav_keywords = ['nav', 'net asset value', 'current nav', 'today nav', 'current price']
        asking_about_nav = any(k in q for k in nav_keywords)
        
        # Find relevant chunks
        relevant_chunks = self.find_relevant_chunks(question, top_k=top_k)
        
        # If asking about NAV, ONLY show expense_information chunks
        if asking_about_nav:
            # Filter to only expense_information chunks
            expense_chunks = [c for c in relevant_chunks if c['chunk'].get('chunk_type') == 'expense_information']
            if expense_chunks:
                # Use only the most relevant expense chunk
                relevant_chunks = [expense_chunks[0]]
            else:
                # Fallback if no expense chunk found
                relevant_chunks = relevant_chunks[:1]
        
        # Check if the question is asking for general definitions/information not in RAG data
        # If very few relevant chunks found (low similarity), assume it's a general query
        if not relevant_chunks or (len(relevant_chunks) > 0 and relevant_chunks[0]['similarity'] < 0.3):
            # General definition question - check if it's about financial terms
            general_keywords = ['what is', 'what are', 'define', 'nav', 'aum', 'expense ratio', 
                               'p/e ratio', 'pb ratio', 'cagr', 'sharpe', 'sortino', 'beta', 'alpha']
            if any(k in q for k in general_keywords):
                response_text = (
                    "I don't have this information in my current database. "
                    "Please visit Groww (https://groww.in/mutual-funds/amc/uti-mutual-funds) "
                    "to know more about mutual fund terms and indicators."
                )
                return {
                    "response": response_text,
                    "sources": [{"url": "https://groww.in/mutual-funds/amc/uti-mutual-funds", 
                                 "fund_name": "Groww - UTI Mutual Funds",
                                 "type": "reference"}]
                }
        
        # Format context
        context = self.format_context_for_gemini(relevant_chunks)
        
        # Generate response
        if self.api_key:
            response_text = self.generate_gemini_response(question, context)
        else:
            response_text = self.generate_basic_response(question, context)
        
        # Format sources - filter by fund name in question
        sources = []
        question_lower = question.lower()
        
        # Extract potential fund names from question (look for multi-word sequences)
        # Check if question mentions a specific fund
        mentioned_funds = []
        for result in relevant_chunks:
            chunk_fund_lower = result['chunk']['fund_name'].lower()
            if chunk_fund_lower in question_lower:
                mentioned_funds.append(chunk_fund_lower)
        
        # If a specific fund was mentioned, only show its sources
        if mentioned_funds:
            for result in relevant_chunks:
                chunk = result['chunk']
                if chunk['fund_name'].lower() in mentioned_funds:
                    sources.append({
                        "fund_name": chunk['fund_name'],
                        "url": chunk['source_url'],
                        "type": chunk['chunk_type']
                    })
        else:
            # Generic query - show all sources
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
            'used_llm': bool(self.api_key)
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
        assistant = WebGeminiFAQAssistant(api_key=api_key)
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
            api_key = os.environ.get('GOOGLE_API_KEY', '')
            assistant = WebGeminiFAQAssistant(api_key=api_key)
            
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
    print("Starting Web Gemini FAQ Assistant...")
    print("Open your browser to http://localhost:5000")
    app.run(debug=True, host='0.0.0.0', port=5000)