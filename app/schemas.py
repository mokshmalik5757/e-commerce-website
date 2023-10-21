from pydantic import BaseModel, StringConstraints, EmailStr, field_validator, model_validator, PositiveFloat
from typing import Annotated, Final
from pydantic_core import PydanticCustomError
import json


class Signup(BaseModel):
    FirstName: Annotated[str, StringConstraints(min_length=3, max_length=20)]
    LastName: Annotated[str, StringConstraints(min_length=3, max_length=20)]
    Email: EmailStr
    UserName: Annotated[str, StringConstraints(min_length=3, max_length=20)]
    Password: Annotated[str, StringConstraints(min_length=3, max_length=20)]
    ConfirmPassword: Annotated[str, StringConstraints(min_length=3, max_length=20)]
    
    @field_validator("FirstName", "LastName", check_fields=True, mode='before') # type: ignore
    @classmethod
    def names_title(cls, name: str) -> str:
        if (name[0].isupper() == False):
            raise PydanticCustomError("Capitilization Error", "Either first letter of FirstName or LastName is not capital")
        
        return name 
    
    @model_validator(mode='after') # type: ignore
    def passwords_match(self) -> "Signup":
        if self.Password is not None and self.ConfirmPassword is not None and self.Password != self.ConfirmPassword:
            raise PydanticCustomError("PasswordsMatchError","Passwords do not match")
        return self
        
    
class ShowSignup(BaseModel):
    message: Final[str] = "Success"
    FirstName: Annotated[str, StringConstraints(min_length=3, max_length=20)]
    LastName: Annotated[str, StringConstraints(min_length=3, max_length=20)]
    Email: EmailStr
    UserName: Annotated[str, StringConstraints(min_length=3, max_length=20)]
    
class UpdateSignup(BaseModel):
    FirstName: Annotated[str, StringConstraints(min_length=3, max_length=20)]
    LastName: Annotated[str, StringConstraints(min_length=3, max_length=20)]
    Email: EmailStr

class TokenData(BaseModel):
    username: str | None = None

class Product(BaseModel):
    Name: Annotated[str, StringConstraints(min_length=2, max_length=20)]
    Price: PositiveFloat
    Description: Annotated[str, StringConstraints(min_length=2, max_length=200)] | None = None
class ShowProduct(BaseModel):
    Name: Annotated[str, StringConstraints(min_length=2, max_length=20)]
    Price: PositiveFloat
    Description: Annotated[str, StringConstraints(min_length=2, max_length=200)] | None = None
    username: str|None = None
class ShowMultipleProducts(BaseModel):
    products: list[ShowProduct]

class Metadatas(BaseModel):
    metadata: list[str] | None = None
    
    @model_validator(mode = "before")
    @classmethod
    def validate_to_json(cls, value):
        if isinstance(value, str):
            return cls(**json.loads(value))
        return value