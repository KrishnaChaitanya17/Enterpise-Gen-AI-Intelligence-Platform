from fastapi import FastAPI
from app.api.routes_chat import router as chat_router
from app.core.exception_handler import global_exception_handler
from app.core.logging_config import setup_logging
from app.core.request_middleware import RequestIDMiddleware

from app.core.limiter import limiter
from slowapi.middleware import SlowAPIMiddleware

from prometheus_client import Counter, Histogram, generate_latest
from fastapi.responses import Response
from fastapi import Request

app = FastAPI(title="Enterprise GenAI Intelligence Platform")

# Logging
setup_logging()

# Exception handler
app.add_exception_handler(Exception, global_exception_handler)

# Request ID Middleware
app.add_middleware(RequestIDMiddleware)

# Rate Limiting
app.state.limiter = limiter
app.add_middleware(SlowAPIMiddleware)

# Prometheus Metrics
REQUEST_COUNT = Counter("request_count", "Total Requests")
REQUEST_LATENCY = Histogram("request_latency_seconds", "Request Latency")

@app.middleware("http")
async def metrics_middleware(request: Request, call_next):
    REQUEST_COUNT.inc()
    with REQUEST_LATENCY.time():
        response = await call_next(request)
    return response

@app.get("/metrics")
async def metrics():
    return Response(generate_latest(), media_type="text/plain")

# Routers
app.include_router(chat_router, prefix="/chat", tags=["Chat"])