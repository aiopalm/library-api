from fastapi import FastAPI

from src.api import auth, books, readers

app = FastAPI(
    title="Library API",
    description="API for library management"
)

app.include_router(auth.router, prefix="/auth", tags=["Authentication"])
app.include_router(books.router, prefix="/books", tags=["Books"])
app.include_router(readers.router, prefix="/readers", tags=["Readers"])