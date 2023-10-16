from dotenv import load_dotenv
load_dotenv()
from fastapi import APIRouter, status, HTTPException
from mysql.connector import pooling
from ..schemas import Signup, ShowSignup, UpdateSignup
from ..hashing import Hash
import mysql.connector
from mysql.connector.errors import Error
from mysql.connector import errorcode
import os

router = APIRouter(prefix="/e-commerce/signup", tags=["SignUp"])
pool = pooling.MySQLConnectionPool(pool_name="Signup_pool", pool_size=3, pool_reset_session=False, host = os.getenv("DB_HOST"), user =os.getenv("DB_USER"),  password = os.getenv("DB_PASSWORD"))

@router.post("/create", status_code=status.HTTP_201_CREATED, response_model=ShowSignup)
async def create_user(signup: Signup):
    try:
        with pool.get_connection() as connection:
            with connection.cursor() as cursor:
                cursor.execute("CREATE DATABASE IF NOT EXISTS ecommerce")
                cursor.execute("USE ecommerce")
                cursor.execute("""
                    CREATE TABLE IF NOT EXISTS users (
                        UserId INT PRIMARY KEY AUTO_INCREMENT UNIQUE,
                        FirstName VARCHAR(255),
                        LastName VARCHAR(255),
                        Email VARCHAR(255),
                        UserName VARCHAR(255) NOT NULL UNIQUE,
                        Password VARCHAR(255)
                    )
                """)
                hash_password = Hash().hash(signup.Password)
                cursor.execute("INSERT INTO users(FirstName, LastName, Email, UserName, Password) VALUES (%s, %s, %s, %s, %s)", (signup.FirstName, signup.LastName, signup.Email, signup.UserName, hash_password))
                connection.commit()
        return signup
    
    except mysql.connector.IntegrityError as err:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail = str(err))
        
@router.get("/get/{username}", status_code=status.HTTP_200_OK)
def get_user(username: str):
        with pool.get_connection() as connection:
            with connection.cursor(buffered=True) as cursor:
                cursor.execute("USE ecommerce")
                cursor.execute("SELECT UserId, FirstName, LastName, Email, UserName FROM users WHERE UserName = %s", (username,))
                user = cursor.fetchone()
                if not user:
                    raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="No such user exists")  
        user = {
            "FirstName": user[1],
            "LastName": user[2],
            "Email": user[3],
            "UserName": user[4]
        }
        return user

@router.put("/change/{username}", status_code=status.HTTP_202_ACCEPTED)
def alter_user(username: str, signup: UpdateSignup):
    with pool.get_connection() as connection:
        with connection.cursor(buffered=True) as cursor:
            cursor.execute("USE ecommerce")
            cursor.execute("UPDATE users SET FirstName = %s, LastName = %s, Email = %s WHERE UserName = %s", (signup.FirstName, signup.LastName, signup.Email, username))
            connection.commit()
            cursor.execute("SELECT UserId, FirstName, LastName, Email, UserName FROM users WHERE UserName = %s", (username,))
            updated_user = cursor.fetchone()            
            if not updated_user:
                raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="No such user exists")
            
            updated_user = {
                "FirstName": updated_user[1],
                "LastName": updated_user[2],
                "Email": updated_user[3],
                "UserName": updated_user[4]
                    }
            return updated_user

@router.delete("/delete/{username}", status_code=status.HTTP_200_OK)
def delete_user(username: str):
    with pool.get_connection() as connection:
        with connection.cursor(buffered = True) as cursor:
            cursor.execute("USE ecommerce")
            cursor.execute("SELECT UserId, FirstName, LastName, Email, UserName FROM users WHERE UserName = %s", (username,))
            user = cursor.fetchone()
            
            if user: 
                cursor.execute("DELETE FROM users where UserName = %s", (username,))
                connection.commit()
                return {"message": f"User {user[4]} deleted successfully"}
            
            if not user:
                raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail='No such user exists')