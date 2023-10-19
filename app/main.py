from fastapi import FastAPI
from app.routers import signup, login, products

app = FastAPI(debug = True, title = "e-commerce")

app.include_router(signup.router)
app.include_router(login.router)
app.include_router(products.router)
