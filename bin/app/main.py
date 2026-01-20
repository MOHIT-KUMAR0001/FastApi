from fastapi import FastAPI
from app.routes import user_route

app = FastAPI()

app.include_router(user_route)
