# Global Exception Middleware

from fastapi import Request
from fastapi.responses import JSONResponse  
from fastapi import status
import traceback
import logging

logger = logging.getLogger("app")

async def global_exception_handler(request: Request, exc: Exception):
    # Log the error with traceback for debugging
    logger.error(f"Unhandled exception: {exc}")
    logger.error(traceback.format_exc())

    # Return a generic error response to the client
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={"error": "Internal server error",
                 "request_id": request.state.request_id if hasattr(request.state, "request_id") else None
                 }  # Include request ID for correlation
    )