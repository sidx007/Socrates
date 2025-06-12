# Socrates Audio Insight

A magical audio transcription, clustering, and summarization web application.

## Overview

Socrates Audio Insight allows users to upload audio files (MP3 or WAV), which are then:
1. **Transcribed** into text using the Deepgram API
2. **Clustered** into related topics through a machine learning backend
3. **Summarized** into concise insights for easy consumption

The frontend features beautiful animations, transitions, and a responsive design for an engaging user experience.

## Setup

### Requirements
- Python 3.8+
- Flask for the frontend server
- FastAPI for the clustering and summarizing backend
- Deepgram API key for audio transcription

### Environment Variables
Set up the necessary API keys:

```bash
# For Windows PowerShell
$env:DEEPGRAM_API_KEY="your_deepgram_api_key"
$env:PERPLEXITY_API_KEY="your_perplexity_api_key"  # For the summarization API
```

### Installation

1. **Frontend Setup**:
   ```bash
   cd frontend
   pip install flask requests werkzeug
   ```

2. **Backend Setup (Clustering API)**:
   ```bash
   cd "../Clustering api"
   pip install -r requirements.txt
   ```

### Running the Application

1. **Start the Backend (Clustering API)**:
   ```bash
   cd "Clustering api"
   uvicorn src.main:app --reload
   ```

2. **Start the Frontend**:
   ```bash
   cd frontend
   python server.py
   ```

3. Open your browser and navigate to `http://localhost:5000`

## Usage

1. **Upload Audio**: Drag and drop or click to upload an MP3 or WAV file
2. **Processing**: Watch as your audio goes through transcription, clustering, and summarization
3. **Results**: View and navigate between:
   - Full transcript
   - Clustered topics
   - Concise summaries

## Technologies

- **Frontend**: HTML, CSS, JavaScript, Flask
- **Backend**: FastAPI, SentenceTransformer, UMAP, HDBSCAN
- **APIs**: Deepgram (transcription), Perplexity (summarization)

## File Structure

```
frontend/
  ├── index.html       # Main web interface
  ├── styles.css       # Styling and animations
  ├── script.js        # Frontend logic
  ├── server.py        # Flask server for handling API requests
  └── convert.py       # Audio transcription module

Clustering api/
  ├── src/
  │   ├── main.py      # FastAPI endpoints for clustering and summarization
  │   └── clusterdata.py # Clustering and summarization logic
  └── requirements.txt
```
