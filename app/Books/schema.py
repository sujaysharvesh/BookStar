import uuid
from datetime import date, datetime
from typing import List
from pydantic import BaseModel
from app.Review.schema import ReviewModel
from typing import Optional
from app.DataBase.models import Review


class Book(BaseModel):
    uid: uuid.UUID
    title: str
    author: str
    publisher: str
    published_date: datetime  
    page_count: int
    language: str  
    created_at: datetime
    update_at: datetime

class BookDeltailModel(Book):
    reviews: Optional[List[ReviewModel]] = None




class BookCreateModel(BaseModel):
    title: str
    author: str
    publisher: str
    published_date: str
    page_count: int
    language: str


class BookUpdateModel(BaseModel):
    title: str
    author: str
    publisher: str
    page_count: int
    language: str