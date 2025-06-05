# semantic_api.py
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import faiss
import numpy as np
import pandas as pd
import os
from sentence_transformers import SentenceTransformer
import uvicorn

# Load config paths
EMBEDDINGS_PATH = "data/embeddings.npy"
INDEX_PATH = "data/faiss_index.faiss"
DATA_PATH = "data/processed_records.parquet"
MODEL_NAME = "sentence-transformers/all-MiniLM-L6-v2"

app = FastAPI()

origins = [
    "https://sawyerbatch.github.io",
    "https://sawyerbatch.github.io/NeurText",
    "http://localhost:5500",
    "http://127.0.0.1:5500"
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Load everything once at startup
print("Loading data and models...")
try:
    df_articles = pd.read_parquet(DATA_PATH)
    embeddings = np.load(EMBEDDINGS_PATH).astype(np.float32)
    index = faiss.read_index(INDEX_PATH)
    model = SentenceTransformer(MODEL_NAME)
    print("Loaded all resources successfully.")
except Exception as e:
    print(f"Failed to load one or more components: {e}")
    raise e

class SearchQuery(BaseModel):
    query: str
    top_k: int = 5

@app.post("/api/semantic-search")
def semantic_search(payload: SearchQuery):
    if not payload.query:
        raise HTTPException(status_code=400, detail="Query cannot be empty")

    try:
        query_embedding = model.encode([payload.query])[0].astype(np.float32)
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

@app.get("/")
def root():
    return {"status": "Semantic Search API online"}

if __name__ == "__main__":
    uvicorn.run("semantic_api:app", host="0.0.0.0", port=8000, reload=True)
