"""
Simple test to check if Flask can find the template
"""

from flask import Flask, render_template

app = Flask(__name__)

@app.route('/')
def index():
    return render_template('simple_ui.html')

if __name__ == '__main__':
    app.run(debug=True, port=5001)