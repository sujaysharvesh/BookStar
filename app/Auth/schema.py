from pydantic import BaseModel, Field
from typing import Optional
from typing import List
from app.DataBase.models import Book, Review
from app.Review.schema import ReviewModel
from pydantic import BaseModel, EmailStr

class UserCreateModel(BaseModel):
    username: str = Field(max_length=8)
    email: str = Field(max_length=40)
    password: str =Field(min_length=8)
    first_name: str = Field(max_length=20)
    last_name: str = Field(max_length=20)

class UserBookModel(UserCreateModel):
    books: Optional[List[Book]] = None  
    reviews: Optional[List[ReviewModel]] = None


class UserLoginModel(BaseModel):
    email: str = Field(max_length=40)
    password: str
    
class MailModel(BaseModel):
    address: EmailStr


class DeleteAccountModel(BaseModel):
    email: str
    password: str
    
class PasswordResetModel(BaseModel):
    email: str

class PasswordResetConfirmModel(BaseModel):
    new_password: str
    confirm_password: str