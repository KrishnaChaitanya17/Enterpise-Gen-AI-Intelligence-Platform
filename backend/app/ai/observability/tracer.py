import time
from app.core.logging import logger


class TraceSpan:

    def __init__(self, trace_id: str, span_name: str):

        self.trace_id = trace_id
        self.span_name = span_name
        self.start_time = None


    def __enter__(self):

        self.start_time = time.time()

        logger.info(
            f"TRACE_ID={self.trace_id} | START {self.span_name}"
        )

        return self


    def __exit__(self, exc_type, exc_val, exc_tb):

        latency = time.time() - self.start_time

        logger.info(
            f"TRACE_ID={self.trace_id} | Span finished: {self.span_name} | latency={latency:.3f}s"
        )