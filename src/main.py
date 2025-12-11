from fastapi import FastAPI

from src.api import auth

app = FastAPI(
    title="Library API",
    description="API for library management"
)

app.include_router(auth.router, prefix="/auth", tags=["Authentication"])
