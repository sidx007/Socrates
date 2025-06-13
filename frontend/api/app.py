import os
import requests
import tempfile
import sys
from pathlib import Path
from flask import Flask, request, jsonify, send_from_directory
from werkzeug.utils import secure_filename

# Try to import CORS, with fallback if not installed
try:
    from flask_cors import CORS
    has_cors = True
except ImportError:
    print("Warning: flask_cors not installed. CORS support disabled.")
    has_cors = False

# Add parent directory to path for imports
sys.path.append(str(Path(__file__).parent.parent))
from convert import transcript

app = Flask(__name__, static_folder="../static", template_folder="../templates")

# Enable CORS if available
if 'has_cors' in locals() and has_cors:
    CORS(app)  # Enable CORS for all routes

# Configuration
UPLOAD_FOLDER = tempfile.gettempdir()
ALLOWED_EXTENSIONS = {'mp3', 'wav'}
# Update with your actual backend API URLs
CLUSTER_API_URL = os.environ.get('CLUSTER_API_URL', "https://e57d-35-223-125-228.ngrok-free.app/cluster")
SUMMARIZE_API_URL = os.environ.get('SUMMARIZE_API_URL', "https://e57d-35-223-125-228.ngrok-free.app/summarize")

app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['MAX_CONTENT_LENGTH'] = 32 * 1024 * 1024  # 32 MB max upload size

def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@app.route('/')
def index():
    return send_from_directory('../templates', 'index.html')

@app.route('/static/<path:path>')
def static_files(path):
    print(f"Serving static file: {path}")
    return send_from_directory('../static', path)

@app.route('/transcribe', methods=['POST'])
def transcribe_audio():
    # Debug info
    print(f"Received transcribe request. Files: {list(request.files.keys())}")
    
    if 'audio' not in request.files:
        print("Error: No 'audio' in request.files")
        return jsonify({'error': 'No audio part'}), 400
    
    file = request.files['audio']
    print(f"File received: {file.filename}, Content type: {file.content_type}")
    
    if file.filename == '':
        print("Error: Empty filename")
        return jsonify({'error': 'No selected file'}), 400
    
    if file and allowed_file(file.filename):
        filename = secure_filename(file.filename)
        filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        print(f"Saving file to: {filepath}")
        file.save(filepath)
        
        try:
            # Call the transcript function from convert.py
            print("Calling transcript function...")
            transcript_text = transcript(filepath)
            print(f"Transcription result: {transcript_text[:100]}...")
            
            # Clean up temporary file
            os.remove(filepath)
            
            if not transcript_text:
                print("Error: Empty transcript text")
                return jsonify({'error': 'Failed to transcribe audio'}), 500
            
            return jsonify({'transcript': transcript_text})
        
        except Exception as e:
            print(f"Exception during transcription: {str(e)}")
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
