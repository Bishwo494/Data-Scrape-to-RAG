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

# semantic search
def semantic_search(query: str, top_k: int = 5):
    query_vec = model.encode([query])
    distances, indices = index.search(query_vec, top_k)
    
    results = []
    for i in indices[0]:
        results.append({
            # 'url': df.iloc[i]['url'],
            'Title': df.iloc[i]['title'],
            'Author': df.iloc[i]['author'],
            # 'book_title': df.iloc[i]['book_title'],
            'Subject': df.iloc[i]['Subject'],
            'html_url': df.iloc[i]['html_url']
            # 'text_url': df.iloc[i]['text_url'],
            # 'search_text': df.iloc[i]['search_text'],
        })
    return results

# url,title,author,book_title,Category,html_url,text_url,search_text

# print(semantic_search("give me fiction books"))


# api route /ask?questionhere&numres=5
@app.get("/ask")
async def ask(
    question: str = Query(..., min_length=3),
    numres: int = Query(5, ge=1, le=50, description="Number of top results to return (max 50)")
):
    try:
        results = semantic_search(question, top_k=numres)
        return JSONResponse(content={
            "answer": f"Top {numres} matches for: '{question}'",
            "sources": results
        })
    except Exception as e:
        return JSONResponse(status_code=500, content={"error": str(e)})