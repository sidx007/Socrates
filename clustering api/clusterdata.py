import os
import requests
from sentence_transformers import SentenceTransformer
import umap.umap_ as umap
from hdbscan import HDBSCAN


def summarize_with_perplexity(text, model="sonar-pro", max_tokens=500, temperature=0.7):
    # 1. Get the key from the environment FIRST.
    api_key = os.environ.get("PERPLEXITY_API_KEY")

    # 2. NOW, check if the key was actually found.
    if not api_key:
        print("Error: PERPLEXITY_API_KEY environment variable not set.")
        return None  # Exit the function if the key is missing

    # The rest of your function remains exactly the same.
    url = "https://api.perplexity.ai/chat/completions"
    payload = {
        "model": model,
        "messages": [
            {"role": "user", "content": f"Summarize the following in brief with appropriate title: {text}"}
        ],
        "max_tokens": max_tokens,
        "temperature": temperature
    }
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json"
    }

    try:
        response = requests.post(url, headers=headers, json=payload)
        response.raise_for_status()
        data = response.json()
        if data.get("choices"):
            return data["choices"][0]["message"]["content"]
        else:
            print("No summary returned.")
            return None
    except requests.exceptions.RequestException as e:
        print(f"An error occurred: {e}")
        if hasattr(e, 'response') and e.response is not None:
            print("Error details:", e.response.text)
        return None



class ClusterData:
    def __init__(self, embedding_model=None, umap_model=None):
        self.embedding_model = embedding_model or SentenceTransformer('thenlper/gte-small')
        self.umap_model = umap_model or umap.UMAP(
            n_components=5, min_dist=0.0, metric='cosine', random_state=42
        )

    def convert_file_to_sentences(self, file):
        transcript = file.decode('utf-8')
        sentences = transcript.split('. ')
        return sentences
    def get_reduced_embeddings(self, sentences):
        embeddings = self.embedding_model.encode(sentences, show_progress_bar=True)
        reduced_embeddings = self.umap_model.fit_transform(embeddings)
        return sentences,reduced_embeddings
    def get_clusters(self, sentences, reduced_embeddings):
        hdbscan_model = HDBSCAN(
            min_cluster_size=20, metric='euclidean', cluster_selection_method='eom'
        ).fit(reduced_embeddings)
        clusters = hdbscan_model.labels_
        cluster_data = []
        for cluster_label in set(clusters):
            if cluster_label != -1:
                sentence_indices = [i for i, label in enumerate(clusters) if label == cluster_label]
                cluster_sentences = [sentences[i] for i in sentence_indices]
                cluster_text = " ".join(cluster_sentences)
                cluster_data.append(cluster_text)  # This line was incorrectly indented
        return cluster_data

    def summarize_clusters(self, cluster_data):
        summaries = []
        for text in cluster_data:  
            summary = summarize_with_perplexity(text)
            if summary:
                summaries.append(summary)
        return summaries
