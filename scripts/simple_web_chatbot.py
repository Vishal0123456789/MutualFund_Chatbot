"""
Simple Web Chatbot without external LLM dependencies
"""

import sys
import json
import os
import pickle
import numpy as np
from pathlib import Path
from datetime import datetime
from typing import List, Dict, Any

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from flask import Flask, render_template, request, jsonify

# Create Flask app with explicit template folder
template_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'templates')
app = Flask(__name__, template_folder=template_dir)

class SimpleWebChatbot:
    def __init__(self, rag_data_path='rag_data/rag_chunks.json'):
        """Initialize simple web chatbot with RAG data"""
        # Resolve the full path to the rag data
        self.rag_data_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', rag_data_path)
        self.chunks = []
        self.conversation_history = []
        self.session_start = datetime.now()
        self.load_data()

    def load_data(self):
        """Load RAG data"""
        print("Loading RAG data...")
        
        # Load chunks from JSON
        with open(self.rag_data_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        # Flatten all chunks into a single list
        self.chunks = []
        for category, category_chunks in data.items():
            for chunk in category_chunks:
                chunk['chunk_type'] = category
                self.chunks.append(chunk)
        
        print(f"Loaded {len(self.chunks)} chunks")

    def find_relevant_chunks(self, question: str) -> List[Dict]:
        """Find relevant chunks using improved keyword matching"""
        relevant_chunks = []
        
        # Convert question to lowercase for case-insensitive matching
        question_lower = question.lower()
        question_words = set(question_lower.split())  # Use set for faster lookup
        
        # Search for relevant chunks based on keywords in the question
        for chunk in self.chunks:
            fund_name = chunk['fund_name'].lower()
            chunk_type = chunk['chunk_type'].lower()
            chunk_data_str = str(chunk['data']).lower()
            
            # Calculate relevance score based on multiple factors
            score = 0
            
            # Check fund name matches
            for word in question_words:
                # Higher weight for exact word matches
                if word in fund_name:
                    score += 3
                if word in chunk_type:
                    score += 2
                if word in chunk_data_str:
                    score += 1
                    
            # Bonus for exact fund name matches
            if any(word in fund_name for word in question_words):
                # Check if this is likely referencing a specific fund
                fund_keywords = ['uti', 'fund', 'elss', 'tax', 'saver', 'growth', 'direct']
                if any(keyword in question_lower for keyword in fund_keywords):
                    score += 2
            
            # Additional bonus for specific question types
            if 'expense' in question_lower and 'expense' in chunk_type:
                score += 3
            elif 'risk' in question_lower and 'risk' in chunk_type:
                score += 3
            elif 'performance' in question_lower and 'performance' in chunk_type:
                score += 3
            elif 'characteristic' in question_lower and 'characteristic' in chunk_type:
                score += 3
            elif 'platform' in question_lower and 'platform' in chunk_type:
                score += 3
            
            # Add chunk if it has significant relevance
            if score > 2:  # Increased threshold for better filtering
                relevant_chunks.append({
                    'chunk': chunk,
                    'similarity': score
                })
        
        # Sort by relevance score (highest first)
        relevant_chunks.sort(key=lambda x: x['similarity'], reverse=True)
        
        # Return top 2 most relevant chunks for better precision
        return relevant_chunks[:2]
    
    def generate_response(self, question: str, relevant_chunks: List[Dict]) -> Dict:
        """Generate a response using relevant chunks"""
        if not relevant_chunks:
            return {
                "response": "I couldn't find relevant information to answer your question. Could you please rephrase or ask about a different topic?",
                "sources": []
            }
        
        # Use only the most relevant chunk for a concise answer
        most_relevant = relevant_chunks[0]
        chunk = most_relevant['chunk']
        
        # Create a concise response focused on the question
        response_parts = []
        sources = []
        
        # Extract specific information based on the question
        question_lower = question.lower()
        
        # Add fund name only if it's relevant to the question
        fund_name_needed = any(keyword in question_lower for keyword in ['fund', 'uti', 'elss', 'tax', 'saver', 'growth', 'direct'])
        if fund_name_needed:
            response_parts.append(f"{chunk['fund_name']}:")
        
        # Extract specific data based on question keywords
        extracted_data = {}
        chunk_data = chunk['data']
        
        # More specific extraction logic
        if ('expense' in question_lower or 'fee' in question_lower) and ('ratio' in question_lower or 'cost' in question_lower):
            if 'expense_ratio' in chunk_data and chunk_data['expense_ratio']:
                extracted_data['Expense Ratio'] = chunk_data['expense_ratio']
        elif 'risk' in question_lower and ('level' in question_lower or 'meter' in question_lower):
            if 'riskometer' in chunk_data and chunk_data['riskometer']:
                extracted_data['Risk Level'] = chunk_data['riskometer']
        elif 'benchmark' in question_lower:
            if 'benchmark' in chunk_data and chunk_data['benchmark']:
                extracted_data['Benchmark'] = chunk_data['benchmark']
        elif ('transaction' in question_lower or 'history' in question_lower or 'statement' in question_lower) and 'download' in question_lower:
            if 'statement_download_info' in chunk_data and chunk_data['statement_download_info']:
                extracted_data['Download Info'] = chunk_data['statement_download_info']
        elif 'nav' in question_lower:
            if 'nav' in chunk_data and chunk_data['nav']:
                extracted_data['NAV'] = chunk_data['nav']
        elif 'sip' in question_lower:
            if 'min_sip' in chunk_data and chunk_data['min_sip']:
                extracted_data['Minimum SIP'] = chunk_data['min_sip']
        elif 'manager' in question_lower:
            if 'fund_manager' in chunk_data and chunk_data['fund_manager']:
                extracted_data['Fund Manager'] = chunk_data['fund_manager']
        elif 'size' in question_lower:
            if 'fund_size' in chunk_data and chunk_data['fund_size']:
                extracted_data['Fund Size'] = chunk_data['fund_size']
        elif 'lock' in question_lower and ('period' in question_lower or 'year' in question_lower):
            if 'lock_in' in chunk_data and chunk_data['lock_in']:
                extracted_data['Lock-in Period'] = chunk_data['lock_in']
        elif 'return' in question_lower:
            if 'fund_returns' in chunk_data and chunk_data['fund_returns']:
                extracted_data['Returns'] = chunk_data['fund_returns']
        else:
            # If no specific match, try to find the most relevant data point
            priority_fields = [
                'expense_ratio', 'riskometer', 'benchmark', 'nav', 'min_sip',
                'fund_manager', 'fund_size', 'lock_in', 'fund_returns'
            ]
            
            for field in priority_fields:
                if field in chunk_data and chunk_data[field]:
                    formatted_key = field.replace('_', ' ').title()
                    extracted_data[formatted_key] = chunk_data[field]
                    break
        
        # Format the extracted data
        if extracted_data:
            for key, value in extracted_data.items():
                if value:  # Only add non-empty values
                    if isinstance(value, dict):
                        response_parts.append(f"{key}:")
                        for sub_key, sub_value in value.items():
                            if sub_value:  # Only add non-empty values
                                response_parts.append(f"  • {sub_key.title()}: {sub_value}")
                    else:
                        response_parts.append(f"{key}: {value}")
        else:
            # Fallback to basic information if nothing specific was found
            response_parts.append("No specific information found for this query.")
        
        # Add source attribution
        source_info = {
            "fund_name": chunk['fund_name'],
            "url": chunk['source_url'],
            "type": chunk['chunk_type']
        }
        sources.append(source_info)
        
        return {
            "response": "\n".join(response_parts) if response_parts else "I couldn't find specific information for your question.",
            "sources": sources
        }

# Global assistant instance
assistant = None

@app.route('/')
def index():
    return render_template('simple_ui.html')

@app.route('/ask', methods=['POST'])
def ask_question():
    global assistant
    try:
        data = request.get_json()
        question = data.get('question', '').strip()
        
        if not question:
            return jsonify({'error': 'No question provided'}), 400
            
        # Initialize assistant if not already done
        if assistant is None:
            assistant = SimpleWebChatbot()
        
        # Find relevant chunks
        relevant_chunks = assistant.find_relevant_chunks(question)
        
        # Generate response
        response = assistant.generate_response(question, relevant_chunks)
        
        # Add to conversation history
        assistant.conversation_history.append({
            'question': question,
            'response': response,
            'timestamp': datetime.now().isoformat()
        })
        
        return jsonify(response)
    except Exception as e:
        import traceback
        traceback.print_exc()
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    print("Starting Simple Web FAQ Assistant...")
    print("Open your browser to http://localhost:5000")
    app.run(debug=True, host='0.0.0.0', port=5000)