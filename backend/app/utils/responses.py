"""Response builders enforcing the documented JSON envelopes."""

from flask import jsonify


def success(data, status=200):
    """Return a ``{"data": ...}`` envelope with the given status code."""
    return jsonify({"data": data}), status


def error_response(code, message, status=400, fields=None):
    """Return an ``{"error": {...}}`` envelope; ``fields`` is omitted when empty."""
    payload = {"code": code, "message": message}
    if fields:
        payload["fields"] = fields
    return jsonify({"error": payload}), status
