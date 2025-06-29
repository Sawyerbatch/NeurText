from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import pandas as pd
import numpy as np
import faiss
from sentence_transformers import SentenceTransformer
import yaml
import os

app = FastAPI()

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "https://sawyerbatch.github.io",
        "https://sawyerbatch.github.io/NeurText",
        "https://sawyerbatch.github.io/NeurText/semantic-search.html",
        "http://localhost:5500",
        "http://127.0.0.1:5500"
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Load config
with open("config.yaml", "r") as f:
    config = yaml.safe_load(f)

paths = config["paths"]
data_path = paths["processed_data"]
embedding_path = paths["embeddings"]
index_path = paths["faiss_index"]

# Lazy-loaded globals
df_articles = None
index = None
model = None

def load_resources():
    global df_articles, index, model
    if df_articles is None:
        df_articles = pd.read_parquet(data_path)
    if index is None:
        index = faiss.read_index(index_path)
    if model is None:
        model = SentenceTransformer(config["embedding_model"]["name"])

# Pydantic input model
class SearchQuery(BaseModel):
    query: str
    top_k: int = config["app_settings"].get("default_top_k", 5)

# Semantic search endpoint
@app.post("/api/semantic-search")
def semantic_search(payload: SearchQuery):
    if not payload.query:
        raise HTTPException(status_code=400, detail="Query cannot be empty")
    try:
        load_resources()
        full_query = config["embedding_model"].get("query_prefix", "") + payload.query
        query_embedding = model.encode([full_query])[0].astype(np.float32)
        D, I = index.search(np.expand_dims(query_embedding, axis=0), payload.top_k)
        results = []
        for idx in I[0]:
            article = df_articles.iloc[idx]
            results.append({
                "id": article.get("id"),
                "title": article.get("title"),
                "abstract": article.get("abstract"),
                "year": article.get("year"),
                "journal": article.get("journal"),
                "authors": article.get("authors")
            })
        return {"results": results}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# Root route
@app.get("/")
def root():
    return {"status": "Semantic Search API online"}
