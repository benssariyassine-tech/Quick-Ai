from flask import Flask, jsonify, render_template, send_from_directory, request
from flask_cors import CORS
import os
import requests

app = Flask(__name__, template_folder='templates', static_folder='static')
CORS(app)


@app.route('/')
def home():
    return render_template('index.html')


@app.route('/static/icon.svg')
def serve_icon():
    return send_from_directory(
        os.path.join(app.root_path, 'static'),
        'icon.svg',
        mimetype='image/svg+xml'
    )


@app.route('/static/manifest.json')
def serve_manifest():
    return send_from_directory(
        os.path.join(app.root_path, 'static'),
        'manifest.json',
        mimetype='application/manifest+json'
    )


@app.route('/static/service-worker.js')
def serve_service_worker():
    response = send_from_directory(
        os.path.join(app.root_path, 'static'),
        'service-worker.js',
        mimetype='application/javascript'
    )
    response.headers['Service-Worker-Allowed'] = '/'
    return response


@app.route('/api/chat', methods=['POST', 'OPTIONS'])
def chat():
    if request.method == 'OPTIONS':
        response = jsonify({})
        response.headers['Access-Control-Allow-Origin'] = '*'
        response.headers['Access-Control-Allow-Methods'] = 'POST, OPTIONS'
        response.headers['Access-Control-Allow-Headers'] = 'Content-Type'
        return response, 204

    try:
        data = request.get_json()
        if not data:
            return jsonify({'error': {'message': 'No data provided'}}), 400

        groq_key = os.environ.get('GROQ_API_KEY', '')
        if not groq_key:
            return jsonify({'error': {'message': 'GROQ_API_KEY not configured'}}), 500

        response = requests.post(
            'https://api.groq.com/openai/v1/chat/completions',
            headers={
                'Authorization': f'Bearer {groq_key}',
                'Content-Type': 'application/json'
            },
            json=data,
            timeout=60
        )

        result = jsonify(response.json())
        result.headers['Access-Control-Allow-Origin'] = '*'
        return result, response.status_code

    except requests.exceptions.Timeout:
        return jsonify({'error': {'message': 'Request timeout'}}), 504
    except Exception as e:
        return jsonify({'error': {'message': str(e)}}), 500


@app.route('/test')
def test():
    return "OK - Quick AI is alive! ✅"


if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)
