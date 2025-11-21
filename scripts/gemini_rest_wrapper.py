"""
Gemini REST API Wrapper - Calls Gemini API directly via HTTP requests
"""

import requests
import json
import sys

def call_gemini_rest(api_key, model_name, prompt):
    """Call Gemini API via REST and return response"""
    try:
        url = f"https://generativelanguage.googleapis.com/v1beta/models/{model_name}:generateContent?key={api_key}"
        
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
        raise Exception(f"Gemini REST API error: {e}")

if __name__ == "__main__":
    try:
        # Get parameters from command line
        api_key = sys.argv[1]
        model_name = sys.argv[2]
        prompt = sys.argv[3]
        
        # Call Gemini and print result
        result = call_gemini_rest(api_key, model_name, prompt)
        print(result)
    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)