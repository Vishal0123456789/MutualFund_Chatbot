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
    
    def format_context_for_gemini(self, relevant_chunks: List[Dict], chunk_type_hint: str = None) -> str:
        """Format context for Gemini prompt with better structure for different data types"""
        if not relevant_chunks:
            return "No relevant information found."
        
        # Detect primary chunk type from relevant chunks
        chunk_types = [c['chunk'].get('chunk_type') for c in relevant_chunks]
        primary_type = chunk_types[0] if chunk_types else None
        
        # Handle expense_information (expense ratio, stamp duty ONLY)
        if primary_type == 'expense_information':
            context_parts = []
            # Only format the FIRST chunk to avoid showing multiple funds
            for result in relevant_chunks[:1]:  # LIMIT TO 1 FUND
                chunk = result['chunk']
                fund_name = chunk['fund_name']
                data = chunk['data']
                
                context_parts.append(f"{fund_name}")
                
                if 'expense_ratio' in data:
                    context_parts.append(f"Expense Ratio: {data['expense_ratio']}")
                
                if 'stamp_duty' in data:
                    context_parts.append(f"Stamp Duty: {data['stamp_duty']}")
                
                context_parts.append(f"Source: {chunk['source_url']}")
            
            return "\n".join(context_parts)
        
        # Handle nav_sip_information (NAV, SIP, Exit Load ONLY)
        elif primary_type == 'nav_sip_information':
            context_parts = []
            # Only format the FIRST chunk to avoid showing multiple funds
            for result in relevant_chunks[:1]:  # LIMIT TO 1 FUND
                chunk = result['chunk']
                fund_name = chunk['fund_name']
                data = chunk['data']
                
                context_parts.append(f"{fund_name}")
                
                if 'nav' in data:
                    nav_date = data.get('nav_date', 'N/A')
                    context_parts.append(f"NAV: ₹{data['nav']} (as of {nav_date})")
                
                if 'min_sip' in data:
                    context_parts.append(f"Minimum SIP: ₹{data['min_sip']}")
                
                if 'exit_load' in data:
                    exit_load = data['exit_load']
                    if exit_load.lower() == 'nil':
                        context_parts.append("Exit Load: None")
                    else:
                        context_parts.append(f"Exit Load: {exit_load}")
                
                context_parts.append(f"Source: {chunk['source_url']}")
            
            return "\n".join(context_parts)
        
        # Handle performance_metrics (P/E, P/B ratios)
        elif primary_type == 'performance_metrics':
            context_parts = []
            # Only format the FIRST chunk to avoid showing multiple funds
            for result in relevant_chunks[:1]:  # LIMIT TO 1 FUND
                chunk = result['chunk']
                fund_name = chunk['fund_name']
                data = chunk['data']
                source = chunk['source_url']
                
                # Create clean format for Gemini
                context_parts.append(f"{fund_name}")
                
                if 'pe_ratio' in data:
                    context_parts.append(f"P/E Ratio: {data['pe_ratio']}")
                if 'pb_ratio' in data:
                    context_parts.append(f"P/B Ratio: {data['pb_ratio']}")
                
                context_parts.append(f"Source: {source}")
            
            return "\n".join(context_parts)
        
        # Handle risk_information
        elif primary_type == 'risk_information':
            context_parts = []
            # Only format the FIRST chunk to avoid showing multiple funds
            for result in relevant_chunks[:1]:  # LIMIT TO 1 FUND
                chunk = result['chunk']
                fund_name = chunk['fund_name']
                data = chunk['data']
                
                context_parts.append(f"{fund_name}")
                context_parts.append("Risk Information")
                
                if 'riskometer' in data:
                    context_parts.append(f"Riskometer: {data['riskometer']}")
                
                if 'risk_metrics' in data:
                    context_parts.append("\nRisk Metrics:")
                    metrics = data['risk_metrics']
                    if isinstance(metrics, dict):
                        for metric_key, metric_value in metrics.items():
                            context_parts.append(f"  {metric_key.upper()}: {metric_value}")
                
                if 'benchmark' in data:
                    context_parts.append(f"\nBenchmark: {data['benchmark']}")
                
                context_parts.append(f"Source: {chunk['source_url']}")
            
            return "\n".join(context_parts)
        
        # Handle fund_characteristics
        elif primary_type == 'fund_characteristics':
            context_parts = []
            # Only format the FIRST chunk to avoid showing multiple funds
            for result in relevant_chunks[:1]:  # LIMIT TO 1 FUND
                chunk = result['chunk']
                fund_name = chunk['fund_name']
                data = chunk['data']
                
                context_parts.append(f"{fund_name}")
                
                if 'fund_size' in data:
                    context_parts.append(f"Fund Size: {data['fund_size']}")
                if 'fund_manager' in data:
                    context_parts.append(f"Fund Manager: {data['fund_manager']}")
                if 'scheme_type' in data:
                    context_parts.append(f"Scheme Type: {data['scheme_type']}")
                if 'sub_category' in data:
                    context_parts.append(f"Category: {data['sub_category']}")
                if 'lock_in' in data:
                    context_parts.append(f"Lock-in Period: {data['lock_in']}")
                
                context_parts.append(f"Source: {chunk['source_url']}")
            
            return "\n".join(context_parts)
        
        # Handle holdings_information
        elif primary_type == 'holdings_information':
            context_parts = []
            for result in relevant_chunks[:1]:  # LIMIT TO 1 FUND
                chunk = result['chunk']
                fund_name = chunk['fund_name']
                data = chunk['data']
                
                context_parts.append(f"{fund_name}")
                context_parts.append("Top Holdings")
                
                if 'top_holdings' in data:
                    for holding in data['top_holdings']:
                        context_parts.append(f"{holding['stock']} {holding['percentage']}")
                
                context_parts.append(f"Source: {chunk['source_url']}")
            
            return "\n".join(context_parts)
        
        # Default formatting for mixed data types
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
            # Detect question type
            q_lower = question.lower()
            is_nav_question = any(k in q_lower for k in ['nav', 'net asset value', 'current price'])
            is_pe_question = any(k in q_lower for k in ['p/e', 'pe ratio', 'p/b', 'pb ratio', 'price to earnings', 'price to book'])
            is_risk_question = any(k in q_lower for k in ['risk', 'riskometer', 'alpha', 'beta', 'sharpe', 'sortino'])
            is_characteristics_question = any(k in q_lower for k in ['fund size', 'fund manager', 'category', 'scheme type'])
            
            # Create dynamic prompt based on question type
            if is_nav_question:
                prompt = f"""Format the NAV (Net Asset Value) information in a clear, well-structured format.

Context:
{context}

Question: {question}

IMPORTANT INSTRUCTIONS:
- ONLY show information for the fund specifically mentioned in the question
- If multiple funds appear in the context but only ONE is asked about, show ONLY that one
- Do NOT list other funds unless explicitly requested
- Format exactly like this example:

UTI ELSS Tax Saver Fund — Direct Growth
Category: ELSS (Equity Linked Savings Scheme)
Key Investment Details
NAV: ₹295.45 (as of 21 Nov 2025)
Minimum SIP: ₹500
Exit Load: None
Cost & Charges
Expense Ratio: 0.91%
Stamp Duty: 0.005%
Source: Groww

Only format the data provided for the REQUESTED fund. Don't add extra funds.
Do NOT add blank lines between items.

Response:"""
            elif is_pe_question or is_risk_question or is_characteristics_question:
                prompt = f"""You are a helpful assistant answering questions about UTI mutual funds.
Use the following context to answer the question accurately.

Context:
{context}

Question: {question}

IMPORTANT: Format your response EXACTLY like this:

Fund Name — Plan Type
P/E Ratio: [value]
P/B Ratio: [value]
Source: [URL]

---

[Repeat for each fund]

Only show information that is requested in the question.
If asking about P/E, only show P/E and P/B ratios in a clean format.
Do NOT show raw context or metadata.
Do NOT repeat fund names multiple times.
Do NOT include "Performance Metrics" or "Source:" labels before the data.
Do NOT add blank lines between items.

Response:"""
            else:
                prompt = f"""You are a helpful assistant answering questions about UTI mutual funds. 
Use the following context to answer the question accurately and concisely.

Context:
{context}

Question: {question}

Please provide a helpful, conversational response based on the context above. 
If the context doesn't contain relevant information, politely say so.
Format your response in a clear, easy-to-read manner.
This is for factual information only. Do not provide investment advice.

Response:"""

            # Using REST API for Gemini calls
            url = f"https://generativelanguage.googleapis.com/v1/models/gemini-pro:generateContent?key={self.api_key}"
            
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
        # BUT allow factual queries about holdings, stocks, and portfolio composition
        holdings_keywords = ['holding', 'holdings', 'stock', 'stocks', 'portfolio', 'composition', 'allocation']
        is_holdings_query = any(k in q for k in holdings_keywords)
        
        advice_keywords = [
            "invest", "buy", "sell", "hold", "recommend", "recommendation",
            "suggest", "allocate", "allocation", "portfolio", "best fund",
            "should i", "advice", "top", "best", "rank", "ranking",
            "outperform", "better than", "worse than", "compare", "comparison"
        ]
        
        # Only block if it's advice-seeking AND not a holdings query
        if not is_holdings_query and any(k in q for k in advice_keywords):
            response_text = (
                "This assistant is designed to provide factual information about UTI Mutual Funds only. "
                "It does not provide investment advice.\n\n"
                "Visit Groww to know more."
            )
            return {
                "response": response_text,
                "sources": [{"url": "https://groww.in/mutual-funds/amc/uti-mutual-funds", 
                             "fund_name": "Groww Platform",
                             "type": "reference"}]
            }
        
        # Detect if user specifies a number of results
        import re
        number_match = re.search(r'(\d+)\s+fund', q)
        top_k = int(number_match.group(1)) if number_match else 10
        top_k = min(top_k, 15)  # Cap at 15 to avoid overwhelming responses
        
        # Determine if question is about NAV - more robust detection
        nav_keywords = ['nav', 'net asset value', 'current nav', 'today nav', 'current price', 'sip', 'exit load', 'minimum sip', 'min sip']
        asking_about_nav = any(k in q for k in nav_keywords)
        
        # Determine if question is about P/E, P/B ratios (performance metrics)
        pe_keywords = ['p/e', 'pe ratio', 'pe ', 'p/b', 'pb ratio', 'pb ', 'price to earnings', 'price to book']
        asking_about_performance = any(k in q for k in pe_keywords)
        
        # Determine if question is about expense ratio, costs
        expense_keywords = ['expense ratio', 'expense', 'cost', 'fee', 'charge', 'stamp duty']
        asking_about_expense = any(k in q for k in expense_keywords)
        
        # Determine if question is about fund manager, characteristics
        characteristics_keywords = ['fund manager', 'manager', 'fund size', 'size', 'category', 'scheme type', 'scheme', 'lock-in', 'lock in', 'lockin']
        asking_about_characteristics = any(k in q for k in characteristics_keywords)
        
        # Determine if question is about risk
        risk_keywords = ['risk', 'riskometer', 'alpha', 'beta', 'sharpe', 'sortino', 'benchmark']
        asking_about_risk = any(k in q for k in risk_keywords)
        
        # Determine if question is about holdings/stocks
        holdings_keywords = ['holding', 'holdings', 'stock', 'stocks', 'portfolio composition', 'top 5', 'top 10', 'top five', 'top ten']
        asking_about_holdings = any(k in q for k in holdings_keywords)
        
        # Find relevant chunks
        relevant_chunks = self.find_relevant_chunks(question, top_k=top_k)
        
        # Filter to only chunks matching the specific fund mentioned in the question
        # Extract fund name patterns from the question
        mentioned_fund = None
        best_match_score = 0
        
        for chunk in relevant_chunks:
            fund_name = chunk['chunk']['fund_name']
            fund_name_lower = fund_name.lower()
            
            # Check if significant parts of the fund name are in the question
            # Split fund name into words and check how many appear in question
            fund_words = [w for w in fund_name_lower.split() if len(w) > 3]  # Skip short words like 'and', 'the'
            matching_words = sum(1 for word in fund_words if word in q)
            
            # If more than half the significant words match, consider it a match
            if len(fund_words) > 0:
                match_score = matching_words / len(fund_words)
                if match_score > 0.5 and match_score > best_match_score:
                    best_match_score = match_score
                    mentioned_fund = fund_name_lower
        
        # If a specific fund was mentioned, filter to only that fund's chunks
        if mentioned_fund:
            relevant_chunks = [c for c in relevant_chunks if c['chunk']['fund_name'].lower() == mentioned_fund]
        
        # Filter by chunk type based on what's being asked
        # Check characteristics first (more specific)
        if asking_about_characteristics:
            # Filter to only fund_characteristics chunks
            char_chunks = [c for c in relevant_chunks if c['chunk'].get('chunk_type') == 'fund_characteristics']
            if char_chunks:
                relevant_chunks = char_chunks[:1]
            else:
                relevant_chunks = relevant_chunks[:1]
        
        elif asking_about_nav:
            # NAV/SIP/Exit Load questions - filter to nav_sip_information chunks
            nav_sip_chunks = [c for c in relevant_chunks if c['chunk'].get('chunk_type') == 'nav_sip_information']
            if nav_sip_chunks:
                relevant_chunks = nav_sip_chunks[:1]
            else:
                relevant_chunks = relevant_chunks[:1]
        
        elif asking_about_expense:
            # Expense ratio questions - filter to expense_information chunks
            expense_chunks = [c for c in relevant_chunks if c['chunk'].get('chunk_type') == 'expense_information']
            if expense_chunks:
                relevant_chunks = expense_chunks[:1]
            else:
                relevant_chunks = relevant_chunks[:1]
        
        # If asking about P/E or P/B, prioritize performance_metrics chunks
        elif asking_about_performance:
            # Filter to only performance_metrics chunks
            perf_chunks = [c for c in relevant_chunks if c['chunk'].get('chunk_type') == 'performance_metrics']
            if perf_chunks:
                relevant_chunks = perf_chunks[:1]
            else:
                relevant_chunks = relevant_chunks[:1]
        
        # If asking about risk
        elif asking_about_risk:
            # Filter to only risk_information chunks
            risk_chunks = [c for c in relevant_chunks if c['chunk'].get('chunk_type') == 'risk_information']
            if risk_chunks:
                relevant_chunks = risk_chunks[:1]
            else:
                relevant_chunks = relevant_chunks[:1]
        
        # If asking about holdings/stocks
        elif asking_about_holdings:
            # Filter to only holdings_information chunks
            holdings_chunks = [c for c in relevant_chunks if c['chunk'].get('chunk_type') == 'holdings_information']
            if holdings_chunks:
                relevant_chunks = holdings_chunks[:1]
            else:
                relevant_chunks = relevant_chunks[:1]
        
        # For other specific queries, limit to relevant chunks
        elif mentioned_fund:
            # Already filtered above - just ensure we don't show too many
            relevant_chunks = relevant_chunks[:3]
        
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
    return render_template('chatbot.html')

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