"""
Gemini Subprocess Wrapper - Runs Gemini API calls in a separate process
"""

import google.generativeai as genai
import sys
import json
import os

def call_gemini(api_key, model_name, prompt):
    """Call Gemini API and return response"""
    try:
        # Configure API key
        genai.configure(api_key=api_key)
        
        # Initialize model
        model = genai.GenerativeModel(model_name)
        
        # Generate response
        response = model.generate_content(prompt)
        return response.text.strip()
    except Exception as e:
        raise Exception(f"Gemini API error: {e}")

if __name__ == "__main__":
    try:
        # Get parameters from command line
        api_key = sys.argv[1]
        model_name = sys.argv[2]
        prompt = sys.argv[3]
        
        # Call Gemini and print result
        result = call_gemini(api_key, model_name, prompt)
        print(result)
    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)