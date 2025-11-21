import os
import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent))

# Set environment variables
os.environ.setdefault('GOOGLE_API_KEY', os.environ.get('GOOGLE_API_KEY', ''))

from scripts.gemini_web_chatbot import app

if __name__ == "__main__":
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=False)
