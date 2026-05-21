from __future__ import annotations

from .admin_content import router as admin_router
from .framework import Application, Route
from .learner_courses import router as learner_router

app = Application(title="nano-lab-academy")
app.include_router(learner_router)
app.include_router(admin_router)


def health() -> dict[str, str]:
    return {"status": "ok"}


app.routes.append(Route(method="GET", path="/", handler=health))


if __name__ == "__main__":
    from wsgiref.simple_server import make_server

    with make_server("127.0.0.1", 8000, app) as server:
        print("Serving on http://127.0.0.1:8000")
        server.serve_forever()
