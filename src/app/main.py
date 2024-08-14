from fastapi import FastAPI

from src.app.routers.transaction import router

app = FastAPI()

@app.get("/")
def read_main():
    return {"message": "Welcome to the Transaction Service API"}

app.include_router(router, prefix="/transaction", tags=["transaction"])
