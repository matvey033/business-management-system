from fastapi import FastAPI

app = FastAPI(
    title="Business Management System",
    description="Финальный проект EffectiveMobile",
    version="0.1.0",
)


@app.get("/ping", tags=["Healthcheck"])
async def ping():
    return {"message": "pong!", "status": "success"}
