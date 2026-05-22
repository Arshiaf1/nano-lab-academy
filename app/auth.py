from __future__ import annotations

import base64
import json
from dataclasses import dataclass
from typing import Any
from urllib.parse import parse_qsl

from .framework import HTTPException, Request


@dataclass(slots=True)
class JwtClaims:
    subject: str | None
    role: str | None
    raw: dict[str, Any]


def _base64url_decode(value: str) -> bytes:
    padding = "=" * (-len(value) % 4)
    return base64.urlsafe_b64decode(value + padding)


def get_bearer_token(request: Request) -> str | None:
    authorization = request.headers.get("Authorization", "")
    if authorization.lower().startswith("bearer "):
        return authorization.split(" ", 1)[1].strip() or None

    cookie_header = request.headers.get("Cookie", "")
    if cookie_header:
        cookies = dict(parse_qsl(cookie_header.replace(";", "&").replace(" ", ""), keep_blank_values=True))
        for key in ("auth_token", "access_token"):
            if cookies.get(key):
                return cookies[key]
    return None


def decode_jwt_claims(token: str) -> JwtClaims:
    parts = token.split(".")
    if len(parts) < 2:
        raise HTTPException(status_code=401, detail="Invalid JWT")

    try:
        payload = json.loads(_base64url_decode(parts[1]).decode("utf-8"))
    except Exception as exc:  # pragma: no cover - defensive fallback
        raise HTTPException(status_code=401, detail="Invalid JWT payload") from exc

    role = payload.get("role")
    if role is None and isinstance(payload.get("roles"), list):
        roles = [str(item) for item in payload["roles"]]
        if roles:
            role = roles[0]

    return JwtClaims(subject=str(payload.get("sub")) if payload.get("sub") is not None else None, role=str(role) if role is not None else None, raw=payload)


def get_request_claims(request: Request) -> JwtClaims:
    token = get_bearer_token(request)
    if token is None:
        raise HTTPException(status_code=401, detail="Missing JWT")
    return decode_jwt_claims(token)


def require_admin(request: Request) -> JwtClaims:
    claims = get_request_claims(request)
    is_admin = claims.role == "admin"
    if not is_admin:
        roles = claims.raw.get("roles")
        if isinstance(roles, list):
            is_admin = any(str(role) == "admin" for role in roles)
    if not is_admin and not claims.raw.get("is_admin", False):
        raise HTTPException(status_code=403, detail="Admin access required")
    return claims
