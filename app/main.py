from fastapi import FastAPI
from .routers import signup, login

app = FastAPI(debug = True, title = "e-commerce")

app.include_router(signup.router)
app.include_router(login.router)
