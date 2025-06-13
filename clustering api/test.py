import requests
import os
import datetime

# Define the API endpoints
url = "https://e57d-35-223-125-228.ngrok-free.app/cluster/"
summarize = "https://e57d-35-223-125-228.ngrok-free.app/summarize/"
a = datetime.datetime.now()
# Path to the text file to send
file_path = "C:\\Users\\User\\Desktop\\LLM\\PRIME\\Socrates\\clustering api\\transcript.txt"

# Prepare the file for upload
with open(file_path, "rb") as file:
    files = {"file": (os.path.basename(file_path), file, "text/plain")}
    response = requests.post(url, files=files)

print("Status Code:", response.status_code)

try:
    output = response.json()
except Exception:
    output = None   
# Send output to summarize endpoint if output is valid
if output:
    summary_response = requests.post(summarize, json=output)
    print("Summary Status Code:", summary_response.status_code)
    try:
        print("Summary JSON:", summary_response.json())
    except Exception:
        print("Summary Text:", summary_response.text)
else:
    print("No output to summarize.")

b = datetime.datetime.now() - a
print(b)