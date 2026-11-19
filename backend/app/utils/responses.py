"""Builders for the shared JSON response envelopes.

Every endpoint in the API answers with one of two shapes::

    {"data": {...}}                                     # success
    {"error": {"code": ..., "message": ...,            # failure
                "fields": {"<field>": "<message>"}}}

The ``fields`` key is omitted entirely when there are no field level errors.
"""

from flask import jsonify

__all__ = ["success", "error_response"]


def success(data, status=200):
    """Return a ``({"data": data}, status)`` tuple for a successful response.

    :param data: JSON serialisable payload placed under the ``data`` key.
    :param status: HTTP status code, defaults to ``200``.
    :returns: ``(flask.Response, int)`` tuple ready to be returned from a view.
    """
    return jsonify({"data": data}), status


def error_response(code, message, status=400, fields=None):
    """Return a ``({"error": {...}}, status)`` tuple for a failed response.

    :param code: Machine readable error code, e.g. ``"VALIDATION_ERROR"``.
    :param message: Human readable description of the problem.
    :param status: HTTP status code, defaults to ``400``.
    :param fields: Optional mapping of ``field -> message``.  When ``None`` or
        empty the ``fields`` key is left out of the payload completely.
    :returns: ``(flask.Response, int)`` tuple ready to be returned from a view.
    """
    payload = {"code": code, "message": message}
    if fields:
        payload["fields"] = dict(fields)
    return jsonify({"error": payload}), status
