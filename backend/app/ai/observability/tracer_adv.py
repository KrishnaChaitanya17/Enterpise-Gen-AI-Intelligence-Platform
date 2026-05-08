import uuid
import time


def start_trace():
    return {
        "trace_id": str(uuid.uuid4()),
        "start_time": time.time(),
        "steps": [],
        "status": "RUNNING",
        "model": None,
        "error": None
    }


def log_step(trace, step_name, meta=None):
    trace["steps"].append({
        "step": step_name,
        "timestamp": time.time(),
        "meta": meta or {}
    })


def end_trace(trace, status="SUCCESS", error=None):
    trace["end_time"] = time.time()
    trace["latency"] = trace["end_time"] - trace["start_time"]
    trace["status"] = status
    trace["error"] = error
    return trace