"""
Debug version of simple web chatbot
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
sys.path.insert(0, str(Path(__file__).parent))

from flask import Flask, render_template, request, jsonify

# Create Flask app with explicit template folder
template_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'templates')
app = Flask(__name__, template_folder=template_dir)

# Simple in-memory storage for testing
assistant = None

class DebugAssistant:
    def __init__(self):
        self.initialized = False
        self.api_key = None
    
    def initialize(self, api_key):
        self.api_key = api_key
        self.initialized = True
        print(f"Assistant initialized with API key: {api_key[:5] if api_key else 'None'}...")

assistant = DebugAssistant()

@app.route('/')
def index():
    try:
        return render_template('simple_ui.html')
    except Exception as e:
        return f"Error loading template: {str(e)}", 500

@app.route('/init', methods=['POST'])
def initialize_assistant():
    global assistant
    try:
        print("Received init request")
        # Get JSON data from request
        data = request.get_json()
        print(f"Request data: {data}")
        
        # Check if data is valid
        if data is None:
            print("Invalid JSON data")
            return jsonify({'status': 'error', 'message': 'Invalid JSON data'}), 400
            
        api_key = data.get('api_key', '').strip()
        print(f"API key: {api_key[:5] if api_key else 'None'}...")
        
        # Initialize assistant with provided API key
        assistant.initialize(api_key)
        print("Assistant initialized successfully")
        return jsonify({'status': 'success', 'message': 'Assistant initialized successfully'})
    except Exception as e:
        import traceback
        traceback.print_exc()
        return jsonify({'status': 'error', 'message': str(e)}), 500

@app.route('/ask', methods=['POST'])
def ask_question():
    global assistant
    try:
        if not assistant.initialized:
            return jsonify({'error': 'Assistant not initialized. Please provide API key first.'}), 400
            
        data = request.get_json()
        question = data.get('question', '').strip()
        
        if not question:
            return jsonify({'error': 'No question provided'}), 400
        
        # Return a simple response for testing
        response_data = {
            "response": f"You asked: {question}",
            "sources": []
        }
        return jsonify(response_data)
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    print("Starting Debug Simple Web FAQ Assistant...")
    print("Template directory:", template_dir)
    print("Open your browser to http://localhost:5003")
    app.run(debug=True, host='0.0.0.0', port=5003)