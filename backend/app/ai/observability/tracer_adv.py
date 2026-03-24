import uuid
import time

def start_trace():
    return {
        "trace_id": str(uuid.uuid4()),
        "start_time": time.time(),
        "steps": []
    }

def log_step(trace, step_name):
    trace["steps"].append({
        "step": step_name,
        "timestamp": time.time()
    })

def end_trace(trace):
    trace["end_time"] = time.time()
    trace["latency"] = trace["end_time"] - trace["start_time"]
    return trace