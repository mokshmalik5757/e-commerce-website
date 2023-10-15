from fastapi import APIRouter, status, HTTPException
from mysql.connector import pooling
from ..schemas import Signup, ShowSignup
from ..hashing import Hash

router = APIRouter(prefix="/e-commerce/signup", tags=["SignUp"])

pool = pooling.MySQLConnectionPool(pool_name="Signup_pool", pool_size=3, pool_reset_session=False, host = 'localhost', user ="root",  password = "password")

@router.post("/create", status_code=status.HTTP_201_CREATED, response_model=ShowSignup)
async def create_user(signup: Signup):
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
                    Password VARCHAR(255)
                )
            """)
            hash_password = Hash().hash(signup.Password)
            cursor.execute("INSERT INTO users(FirstName, LastName, Email, Password) VALUES (%s, %s, %s, %s)", (signup.FirstName, signup.LastName, signup.Email, hash_password))
            connection.commit()
    return signup
        
@router.get("/get/{email}", status_code=status.HTTP_200_OK)
def get_user(email: str):
    with pool.get_connection() as connection:
        with connection.cursor(buffered=True) as cursor:
            cursor.execute("USE ecommerce")
            cursor.execute("SELECT UserId, FirstName, LastName, Email FROM users WHERE Email = %s", (email,))
            user = cursor.fetchone()
            if not user:
                raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="No such user exists")  
    user = {
        "FirstName": user[1],
        "LastName": user[2],
        "Email": user[3]
    }
    return user
    