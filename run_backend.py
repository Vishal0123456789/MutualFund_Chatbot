
import os
os.environ['GOOGLE_API_KEY'] = 'AIzaSyAnvxpG83yA9w6iy-RSJbQbGZRU2D74AA4'

from scripts.gemini_web_chatbot import app

if __name__ == '__main__':
    app.run(debug=False, host='0.0.0.0', port=5000)
