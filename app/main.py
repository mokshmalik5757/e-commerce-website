from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.routers import signup, login, products

app = FastAPI(debug = True, title = "e-commerce")

origins = ["*"]

app.add_middleware(
    CORSMiddleware,
    allow_origins = origins,
    allow_credentials = True,
    allow_methods = ["*"],
    allow_headers = ["*"]
)

app.include_router(signup.router)
app.include_router(login.router)
app.include_router(products.router)

@app.get("/", tags=["Health Check"], status_code=200)
def health_check():
    return {"message": "Server is working fine"}