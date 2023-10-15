from fastapi import FastAPI
from .routers import signup

app = FastAPI(debug = True, title = "e-commerce")

app.include_router(signup.router)

