import os
import requests
import tempfile
from flask import Flask, request, jsonify, send_from_directory
from werkzeug.utils import secure_filename
from convert import transcript

app = Flask(__name__, static_folder=".")

# Configuration
UPLOAD_FOLDER = tempfile.gettempdir()
ALLOWED_EXTENSIONS = {'mp3', 'wav'}
CLUSTER_API_URL = "http://localhost:8000/cluster"
SUMMARIZE_API_URL = "http://localhost:8000/summarize"

app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['MAX_CONTENT_LENGTH'] = 32 * 1024 * 1024  # 32 MB max upload size

def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@app.route('/')
def index():
    return send_from_directory('.', 'index.html')

@app.route('/<path:path>')
def static_files(path):
    return send_from_directory('.', path)

@app.route('/transcribe', methods=['POST'])
def transcribe_audio():
    if 'audio' not in request.files:
        return jsonify({'error': 'No audio part'}), 400
    
    file = request.files['audio']
    
    if file.filename == '':
        return jsonify({'error': 'No selected file'}), 400
    
    if file and allowed_file(file.filename):
        filename = secure_filename(file.filename)
        filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        file.save(filepath)
        
        try:
            # Call the transcript function from convert.py
            transcript_text = transcript(filepath)
            
            # Clean up temporary file
            os.remove(filepath)
            
            if not transcript_text:
                return jsonify({'error': 'Failed to transcribe audio'}), 500
            
            return jsonify({'transcript': transcript_text})
        
        except Exception as e:
            # Clean up if error occurs
            if os.path.exists(filepath):
                os.remove(filepath)
            return jsonify({'error': str(e)}), 500
    
    return jsonify({'error': 'File type not allowed'}), 400

@app.route('/cluster', methods=['POST'])
def cluster_text():
    if 'file' not in request.files:
        return jsonify({'error': 'No text file part'}), 400
    
    file = request.files['file']
    
    if file.filename == '':
        return jsonify({'error': 'No selected file'}), 400
    
    try:
        # Forward the request to the clustering API
        files = {'file': (file.filename, file.stream, 'text/plain')}
        response = requests.post(CLUSTER_API_URL, files=files)
        response.raise_for_status()
        
        return jsonify(response.json())
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/summarize', methods=['POST'])
def summarize_clusters():
    try:
        # Get clusters from request
        clusters = request.json
        if not clusters:
            return jsonify({'error': 'No clusters provided'}), 400
        
        # Forward the request to the summarize API
        response = requests.post(SUMMARIZE_API_URL, json=clusters)
        response.raise_for_status()
        
        return jsonify(response.json())
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True, port=5000)
