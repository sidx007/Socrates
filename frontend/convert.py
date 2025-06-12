import requests
import os

# Get API key from environment variable 
DEEPGRAM_API_KEY = os.environ.get('DEEPGRAM_API_KEY')

def transcript(file_path):
    if not DEEPGRAM_API_KEY:
        raise ValueError("DEEPGRAM_API_KEY environment variable is not set")
        
    API_URL = "https://api.deepgram.com/v1/listen"
    headers = {
        "Authorization": f"Token {DEEPGRAM_API_KEY}",
        "Content-Type": "audio/wav"
    }
    params = {
        "model": "nova-2",
        "smart_format": "true"
    }

    try:
        with open(file_path, 'rb') as audio:
            response = requests.post(API_URL, headers=headers, params=params, data=audio)
            response.raise_for_status()
            result = response.json()
            return result['results']['channels'][0]['alternatives'][0]['transcript']
    except requests.exceptions.RequestException as e:
        print(f"Error transcribing {file_path}: {e}")
        if e.response:
            print(f"  - API Response: {e.response.text}")
        return ""
    except KeyError:
        print(f"  - Could not parse transcript from Deepgram response for {file_path}.")
        return ""