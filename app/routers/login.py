from dotenv import load_dotenv
load_dotenv()
from fastapi import APIRouter, status, HTTPException, Depends
from fastapi.security import OAuth2PasswordRequestForm
from mysql.connector import pooling
import os
from app.hashing import Hash
from app.token import create_access_token

router = APIRouter(prefix = "/e-commerce/login", tags=["Login"])

connection_pool = pooling.MySQLConnectionPool(pool_name="LoginPool", pool_size=5, host = os.getenv("DB_HOST"), user = os.getenv("DB_USER"), password = os.getenv("DB_PASSWORD"))

@router.post("/", status_code=status.HTTP_200_OK)
async def get_login(login: OAuth2PasswordRequestForm = Depends()):
    with connection_pool.get_connection() as connection:
        with connection.cursor() as cursor:
            cursor.execute("USE ecommerce;")
            cursor.execute("SELECT UserName, Password FROM users WHERE UserName = %s", (login.username,))
            login_user = cursor.fetchone()
            if login_user:
                if Hash.verify_passwords(login.password, login_user[1]) == True:
                    access_token = create_access_token(data={"sub": login.username})
                    return {"message": f"Login successful for user {login_user[0]}", "access_token": access_token, "token_type":"bearer"}

            if not login_user:
                raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Invalid Credentials")

    