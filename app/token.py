from dotenv import load_dotenv
load_dotenv()
import os
from datetime import datetime, timedelta
from jose import jwt, JWTError
from app.schemas import TokenData

SECRET_KEY = os.environ["TOKEN_SECRET"]
ALGORITHM = os.environ["TOKEN_ALGORITHM"]
ACCESS_TOKEN_EXPIRE_MINUTES = 30

def create_access_token(data: dict):
    to_encode = data.copy()
    expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

def verify_token(token:str, credentials_exception):
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username = payload.get("sub")
        if username is None:
            raise credentials_exception
        token_data = TokenData(username=username)
        return token_data
    
    except JWTError:
        raise credentials_exception