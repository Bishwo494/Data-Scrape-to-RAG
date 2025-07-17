cd /home/docker/notebooks/fastapi
python3 -m uvicorn main:app --host 0.0.0.0 --port 10000 --reload

echo "FastAPI server is running at http://localhost:10000"