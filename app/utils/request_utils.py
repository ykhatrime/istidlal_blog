"""Request related helpers."""
from flask import request


def client_ip() -> str | None:
    forwarded = request.headers.get('X-Forwarded-For')
    if forwarded:
        return forwarded.split(',')[0].strip()
    return request.remote_addr
