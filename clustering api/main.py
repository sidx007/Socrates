from fastapi import FastAPI, File, UploadFile
from fastapi.responses import JSONResponse
from typing import List
from clusterdata import ClusterData

app = FastAPI(title="Socrates Clustering API")

@app.get("/")
async def root():
    return {"message": "Socrates Clustering API is running"}

@app.get("/health")
async def health_check():
    return {"status": "healthy"}

@app.post("/cluster")
async def cluster_text(file: UploadFile = File(...)):
    """
    Cluster the provided text into sentences and return the clustered sentences.
    """
    cluster_method = ClusterData()
    if not file.filename.endswith(".txt"):
        return JSONResponse(status_code=400, content={"error": "Only .txt files are allowed"})
    text = await file.read()
    sentences = cluster_method.convert_file_to_sentences(text)
    sentences, reduced_embeddings = cluster_method.get_reduced_embeddings(sentences)
    clusters = cluster_method.get_clusters(sentences, reduced_embeddings)
    return {"clusters": clusters}

@app.post("/summarize")
async def summarize_text(clusters: List[str]):
    """
    Summarize the provided text clusters.
    """
    cluster_method = ClusterData()
    if not clusters:
        return JSONResponse(status_code=400, content={"error": "No clusters provided"})
    summaries = cluster_method.summarize_clusters(clusters)
    return {"summaries": summaries}
