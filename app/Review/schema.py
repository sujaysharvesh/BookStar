from pydantic import BaseModel, Field
import uuid
from typing import Optional
from datetime import datetime

class ReviewModel(BaseModel):
    uid: uuid.UUID 
    user_id: Optional[uuid.UUID] 
    book_uid: Optional[uuid.UUID] 
    review: str 
    rating: int = Field(le=5, ge=1)
    created_at: datetime 
    updated_at: datetime 
    
class ReviewCreateModel(BaseModel):
    review: str 
    rating: int = Field(le=5, ge=1)
    
class ReviewUpdateMOdel(BaseModel):
    review: str
    rating: int = Field(le=5, ge=1)