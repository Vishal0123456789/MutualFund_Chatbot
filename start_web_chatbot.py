"""
Simple startup script for the web chatbot
"""

import os
import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent))

def main():
    print("Starting Web FAQ Assistant...")
    print("Make sure you have installed the required dependencies:")
    print("  pip install flask")
    print()
    print("Starting the web server...")
    print("Open your browser to http://localhost:5000")
    print()
    
    # Import and run the web chatbot
    try:
        from scripts.web_chatbot import app
        app.run(debug=True, host='0.0.0.0', port=5000)
    except ImportError as e:
        print(f"Error importing web chatbot: {e}")
        print("Make sure all dependencies are installed.")
        sys.exit(1)
    except Exception as e:
        print(f"Error starting web chatbot: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()