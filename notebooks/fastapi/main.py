from fastapi import FastAPI, Query
from fastapi.responses import JSONResponse
import pandas as pd
import faiss
from sentence_transformers import SentenceTransformer

"""
package to install if not already installed:
fastapi
uvicorn
"""

app = FastAPI()

#load on server start
df = pd.read_csv('/home/docker/notebooks/data/metadata_random_ebooks_metadata.csv')
index = faiss.read_index('/home/docker/notebooks/data/faiss_index.bin')
model = SentenceTransformer('all-MiniLM-L6-v2')

#semantic search
def semantic_search(query: str, top_k: int = 5):
    query_vec = model.encode([query])
    distances, indices = index.search(query_vec, top_k)
    
    results = []
    for i in indices[0]:
        results.append({
            'Title': df.iloc[i]['Title'],
            'Author': df.iloc[i]['Author'],
            'EBook-No.': int(df.iloc[i]['EBook-No.']),
            'Subject': df.iloc[i]['Subject'],
        })
    return results




# # api route /ask?questionhere&numres=5
# @app.get("/ask")
# async def ask(
#     question: str = Query(..., min_length=3),
#     numres: int = Query(5, ge=1, le=50, description="Number of top results to return (max 50)")
# ):
#     try:
#         results = semantic_search(question, top_k=numres)
#         return JSONResponse(content={
#             "answer": f"Top {numres} matches for: '{question}'",
#             "sources": results
#         })
#     except Exception as e:
#         return JSONResponse(status_code=500, content={"error": str(e)})