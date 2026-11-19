"""Health check endpoint."""

from flask import Blueprint

from ..utils.responses import success

health_bp = Blueprint("health", __name__, url_prefix="/api/v1")


@health_bp.get("/health")
def health():
    """Return a simple liveness payload."""
    return success({"status": "ok"})
