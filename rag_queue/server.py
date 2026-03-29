from fastapi import FastAPI, Query, Path, HTTPException
from rq.job import Job
from rq.exceptions import NoSuchJobError

try:
    from .clients.rq_client import queue
    from .queues.worker import process_query
except ImportError:
    # Allow running via `python main.py` from the `rag_queue` directory.
    from clients.rq_client import queue
    from queues.worker import process_query


from dotenv import load_dotenv

load_dotenv()

app = FastAPI()


@app.get("/")
def root():
    return {"message": "Hello World"}

@app.post('/chat')
def chat( query : str = Query(..., description="The chat query of user")):
    job = queue.enqueue(process_query,query)

    return {"job_id": job.id, "status": job.get_status()}

@app.get('/chat/{job_id}')
def get_result(
    job_id: str = Query(..., description="Job id to fetch the result for")
):
    