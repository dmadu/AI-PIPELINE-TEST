"""Health-check endpoint.

The success envelope is built with the shared ``app.utils.responses.success`` helper when it is
available; until that module lands (later Phase 1 task) an inline equivalent producing the exact
same ``{"data": {...}}`` body is used, so swapping it changes no response.
"""

from flask import Blueprint, jsonify

try:  # pragma: no cover - exercised once app/utils/responses.py exists.
    from ..utils.responses import success
except ImportError:  # pragma: no cover - current Phase 1 state.

    def success(data, status=200):
        """Return the standard ``{"data": ...}`` success envelope."""
        return jsonify({"data": data}), status


health_bp = Blueprint("health", __name__, url_prefix="/api/v1")


@health_bp.get("/health")
def get_health():
    """Report that the API process is up and able to serve requests."""
    return success({"status": "ok", "service": "backend", "version": "v1"})
