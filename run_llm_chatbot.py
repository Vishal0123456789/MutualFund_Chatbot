"""
Launcher script for LLM-enhanced chatbot with API key
"""

import os
import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent))

def main():
    # Set your OpenAI API key here
    api_key = "your_actual_api_key_here"  # <-- Replace with your actual API key
    
    if api_key and api_key != "your_actual_api_key_here":
        os.environ['OPENAI_API_KEY'] = api_key
        print("OpenAI API key set from launcher script")
    else:
        print("Warning: No API key found in launcher script")
        print("Please set OPENAI_API_KEY environment variable or add your key to this script")
    
    # Import and run the LLM chatbot
    try:
        from scripts.llm_enhanced_chatbot import main as chatbot_main
        chatbot_main()
    except ImportError as e:
        print(f"Error importing LLM chatbot: {e}")
        sys.exit(1)
    except Exception as e:
        print(f"Error starting LLM chatbot: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()