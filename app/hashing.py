from passlib.context import CryptContext
crypt_password = CryptContext(schemes=["bcrypt"], deprecated = "auto")
class Hash:
    
    @staticmethod
    def hash(password: str):
        return crypt_password.hash(password)
    
    @staticmethod
    def verify_passwords(plain_password: str, hashed_password:str):
        return crypt_password.verify(plain_password, hashed_password)