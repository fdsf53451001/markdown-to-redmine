"""
Flask web application for Redmine <-> Markdown conversion.
"""
import os
from flask import Flask, render_template, request, jsonify
from converter import redmine_to_markdown, markdown_to_redmine

app = Flask(__name__)


@app.route('/')
def index():
    """Render the main page."""
    return render_template('index.html')


@app.route('/api/convert', methods=['POST'])
def convert():
    """API endpoint for conversion."""
    data = request.get_json()

    if not data:
        return jsonify({'error': 'No data provided'}), 400

    text = data.get('text', '')
    direction = data.get('direction', 'redmine_to_markdown')

    try:
        if direction == 'redmine_to_markdown':
            result = redmine_to_markdown(text)
        elif direction == 'markdown_to_redmine':
            result = markdown_to_redmine(text)
        else:
            return jsonify({'error': 'Invalid direction'}), 400

        return jsonify({'result': result})
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/health')
def health():
    """Health check endpoint for Cloud Run."""
    return jsonify({'status': 'healthy'})


if __name__ == '__main__':
    port = int(os.environ.get('PORT', 8080))
    app.run(host='0.0.0.0', port=port, debug=False)
