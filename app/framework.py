from __future__ import annotations

import inspect
import json
import re
from dataclasses import dataclass
from typing import Any, Callable
from typing import get_type_hints
from urllib.parse import parse_qs


class HTTPException(Exception):
    def __init__(self, status_code: int, detail: str) -> None:
        super().__init__(detail)
        self.status_code = status_code
        self.detail = detail


@dataclass(slots=True)
class Route:
    method: str
    path: str
    handler: Callable[..., Any]


@dataclass(slots=True)
class Request:
    method: str
    path: str
    query_params: dict[str, str]
    headers: dict[str, str]
    environ: dict[str, Any]
    body: dict[str, Any]


class Router:
    def __init__(self, prefix: str = "") -> None:
        self.prefix = prefix.rstrip("/")
        self.routes: list[Route] = []

    def add_route(self, method: str, path: str) -> Callable[[Callable[..., Any]], Callable[..., Any]]:
        normalized_path = path if path.startswith("/") else f"/{path}"

        def decorator(handler: Callable[..., Any]) -> Callable[..., Any]:
            self.routes.append(Route(method.upper(), f"{self.prefix}{normalized_path}", handler))
            return handler

        return decorator

    def get(self, path: str) -> Callable[[Callable[..., Any]], Callable[..., Any]]:
        return self.add_route("GET", path)

    def post(self, path: str) -> Callable[[Callable[..., Any]], Callable[..., Any]]:
        return self.add_route("POST", path)


class Application:
    def __init__(self, title: str = "app") -> None:
        self.title = title
        self.routes: list[Route] = []

    def include_router(self, router: Router) -> None:
        self.routes.extend(router.routes)

    def route_paths(self) -> list[str]:
        return [route.path for route in self.routes]

    def __call__(self, environ: dict[str, Any], start_response: Callable[..., Any]) -> list[bytes]:
        method = environ.get("REQUEST_METHOD", "GET").upper()
        raw_path = environ.get("PATH_INFO", "") or "/"
        query_params = {key: values[0] if values else "" for key, values in parse_qs(environ.get("QUERY_STRING", "")).items()}
        body = self._read_json_body(environ)
        request = Request(
            method=method,
            path=raw_path,
            query_params=query_params,
            headers=self._extract_headers(environ),
            environ=environ,
            body=body,
        )

        for route in self.routes:
            path_params = self._match(route.path, raw_path)
            if path_params is None or route.method != method:
                continue

            try:
                response = self._invoke(route.handler, path_params, query_params, body, request)
                status_code = 200
            except HTTPException as exc:
                status_code = exc.status_code
                response = {"detail": exc.detail}
            except Exception as exc:  # pragma: no cover - defensive fallback
                status_code = 500
                response = {"detail": str(exc)}

            response, response_status_code, content_type_override = self._unwrap_response(response)
            if response_status_code is not None:
                status_code = response_status_code

            payload, content_type = self._serialize_response(response, content_type_override)
            start_response(f"{status_code} {'OK' if status_code < 400 else 'ERROR'}", [("Content-Type", content_type), ("Content-Length", str(len(payload)))])
            return [payload]

        payload = json.dumps({"detail": "Not found"}).encode("utf-8")
        start_response("404 ERROR", [("Content-Type", "application/json; charset=utf-8"), ("Content-Length", str(len(payload)))])
        return [payload]

    def _unwrap_response(self, response: Any) -> tuple[Any, int | None, str | None]:
        if not isinstance(response, tuple):
            return response, None, None

        if len(response) == 2:
            body, status_code = response
            return body, int(status_code), None

        if len(response) == 3:
            body, status_code, content_type = response
            return body, int(status_code), str(content_type)

        return response, None, None

    def _serialize_response(self, response: Any, content_type_override: str | None = None) -> tuple[bytes, str]:
        if isinstance(response, bytes):
            return response, content_type_override or "application/octet-stream"
        if isinstance(response, str):
            return response.encode("utf-8"), content_type_override or "text/html; charset=utf-8"
        return json.dumps(response, default=str).encode("utf-8"), content_type_override or "application/json; charset=utf-8"

    def _invoke(
        self,
        handler: Callable[..., Any],
        path_params: dict[str, Any],
        query_params: dict[str, Any],
        body: dict[str, Any],
        request: Request,
    ) -> Any:
        signature = inspect.signature(handler)
        type_hints = get_type_hints(handler)
        values: dict[str, Any] = {**query_params, **path_params}

        if "payload" in signature.parameters:
            values["payload"] = body
        if "request" in signature.parameters:
            values["request"] = request
        if "environ" in signature.parameters:
            values["environ"] = request.environ

        filtered: dict[str, Any] = {}
        for name, parameter in signature.parameters.items():
            if name not in values:
                continue
            value = values[name]
            annotation = type_hints.get(name, parameter.annotation)
            if annotation is int or annotation == int or annotation == "int":
                value = int(value)
            filtered[name] = value

        return handler(**filtered)

    def _match(self, pattern: str, path: str) -> dict[str, Any] | None:
        escaped = re.sub(r"\{([^/{}]+)\}", r"(?P<\1>[^/]+)", pattern.rstrip("/"))
        regex = re.compile(f"^{escaped}$")
        match = regex.match(path.rstrip("/"))
        if match is None:
            return None
        return match.groupdict()

    def _read_json_body(self, environ: dict[str, Any]) -> dict[str, Any]:
        if environ.get("REQUEST_METHOD", "GET").upper() not in {"POST", "PUT", "PATCH"}:
            return {}

        try:
            content_length = int(environ.get("CONTENT_LENGTH") or 0)
        except ValueError:
            content_length = 0

        if content_length <= 0:
            return {}

        body_bytes = environ["wsgi.input"].read(content_length)
        if not body_bytes:
            return {}

        return json.loads(body_bytes.decode("utf-8"))

    def _extract_headers(self, environ: dict[str, Any]) -> dict[str, str]:
        headers: dict[str, str] = {}
        for key, value in environ.items():
            if not isinstance(value, str):
                continue
            if key.startswith("HTTP_"):
                header_name = key[5:].replace("_", "-").title()
                headers[header_name] = value
            elif key in {"CONTENT_TYPE", "CONTENT_LENGTH"}:
                headers[key.replace("_", "-").title()] = value
        return headers
