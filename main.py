from fastapi import FastAPI
from fastapi.responses import JSONResponse

app = FastAPI(
    title="Nano Lab Academy Backend",
    description="FastAPI backend for Nano Lab Academy",
    version="1.0.0"
)


@app.get("/api/health")
async def health_check():
    return JSONResponse({"status": "ok"})


@app.get("/")
async def root():
    return {"message": "Nano Lab Academy Backend is running"}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=True
    )
