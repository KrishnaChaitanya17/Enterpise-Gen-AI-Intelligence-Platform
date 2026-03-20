import uuid
import asyncio

jobs = {}


async def run_ingestion_job(job_id, folder_path):
    from app.ai.ingestion.multi_loader import load_documents
    from app.ai.ingestion.embedder import embed_documents
    from app.ai.ingestion.vector_store import add_documents_to_vector_db

    try:
        jobs[job_id]["status"] = "running"

        docs = load_documents(folder_path)

        add_documents_to_vector_db(docs)

        jobs[job_id]["status"] = "completed"

    except Exception as e:
        jobs[job_id]["status"] = "failed"
        jobs[job_id]["error"] = str(e)


def create_ingestion_job(folder_path):
    job_id = str(uuid.uuid4())

    jobs[job_id] = {
        "status": "queued",
        "folder": folder_path
    }

    asyncio.create_task(run_ingestion_job(job_id, folder_path))

    return job_id


def get_job_status(job_id):
    return jobs.get(job_id, {"status": "not_found"})