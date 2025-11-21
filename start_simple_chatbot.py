"""
Simple startup script for the simple web chatbot
"""

import os
import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent))

def main():
    print("Starting Simple Web FAQ Assistant...")
    print("Make sure you have installed the required dependencies:")
    print("  pip install flask")
    print()
    print("Starting the web server...")
    print("Open your browser to http://localhost:5000")
    print("Template directory:", os.path.join(os.path.dirname(__file__), 'templates'))
    print("Data directory:", os.path.join(os.path.dirname(__file__), 'rag_data'))
    print()
    
    # Import and run the simple web chatbot
    try:
        from scripts.simple_web_chatbot import app
        app.run(debug=True, host='0.0.0.0', port=5000)
    except ImportError as e:
        print(f"Error importing simple web chatbot: {e}")
        print("Make sure all dependencies are installed:")
        print("  pip install flask")
        sys.exit(1)
    except Exception as e:
        print(f"Error starting simple web chatbot: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

if __name__ == "__main__":
    main()