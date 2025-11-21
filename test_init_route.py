"""
Simple test for the init route
"""

from flask import Flask, request, jsonify

app = Flask(__name__)

@app.route('/')
def index():
    return '''
    <html>
    <body>
        <h1>Test Init Route</h1>
        <input type="text" id="api_key" placeholder="Enter API Key">
        <button onclick="testInit()">Test Init</button>
        <div id="result"></div>
        
        <script>
        async function testInit() {
            const apiKey = document.getElementById('api_key').value;
            try {
                const response = await fetch('/init', {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json',
                    },
                    body: JSON.stringify({ api_key: apiKey })
                });
                
                const data = await response.json();
                document.getElementById('result').innerHTML = '<pre>' + JSON.stringify(data, null, 2) + '</pre>';
            } catch (error) {
                document.getElementById('result').innerHTML = '<p>Error: ' + error.message + '</p>';
                console.error('Error:', error);
            }
        }
        </script>
    </body>
    </html>
    '''

@app.route('/init', methods=['POST'])
def initialize_assistant():
    try:
        # Get JSON data from request
        data = request.get_json()
        
        # Check if data is valid
        if data is None:
            return jsonify({'status': 'error', 'message': 'Invalid JSON data'}), 400
            
        api_key = data.get('api_key', '').strip()
        
        return jsonify({'status': 'success', 'message': f'API key received: {api_key[:5]}...'})
    except Exception as e:
        import traceback
        traceback.print_exc()
        return jsonify({'status': 'error', 'message': str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True, port=5002)