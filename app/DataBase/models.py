from sqlmodel import SQLModel, Field, Column, Relationship
import sqlalchemy.dialects.postgresql as pg
import uuid
from sqlalchemy import func
from datetime import datetime
from typing import Optional, List


class User(SQLModel, table=True):
    __tablename__ = "users"

    uid: uuid.UUID = Field(
        sa_column=Column(pg.UUID, default=uuid.uuid4, primary_key=True, nullable=False, unique=True)
    )
    username: str = Field(sa_column=Column(pg.VARCHAR(255), nullable=False, unique=True))
    first_name: str = Field(sa_column=Column(pg.VARCHAR(255), nullable=False))
    last_name: str = Field(sa_column=Column(pg.VARCHAR(255), nullable=False))
    email: str = Field(sa_column=Column(pg.VARCHAR(255), nullable=False, unique=True))
    password: str = Field(sa_column=Column(pg.VARCHAR(255), nullable=False))
    rol: str = Field(sa_column=Column(pg.VARCHAR, nullable=False, server_default="user"))
    created_at: datetime = Field(sa_column=Column(pg.TIMESTAMP, default=datetime.now))
    is_verified: bool = Field(sa_column=Column(pg.BOOLEAN, default=False))
    books: List["Book"] = Relationship(
        back_populates="user", sa_relationship_kwargs={"lazy": "selectin"}
    )
    reviews: List["Review"] = Relationship(
        back_populates="user", sa_relationship_kwargs={"lazy": "selectin"}
    )

    def __repr__(self):
        return f"<User {self.username}>"

class BookTag(SQLModel, table=True):
    book_id: uuid.UUID = Field(default=None, foreign_key="books.uid", primary_key=True)
    tag_id: uuid.UUID = Field(default=None, foreign_key="tags.uid", primary_key=True)

class Tag(SQLModel, table=True):
    __tablename__='tags'
    uid: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    name: str = Field(nullable=False)
    created_at: datetime = Field(default=datetime.now)
    books: List["Book"] = Relationship(
        link_model=BookTag,  
        back_populates="tags", 
        sa_relationship_kwargs={"lazy": "selectin"}
    )

    def __repr__(self) -> str:
        return f"<Tag {self.name}>"
    

class Book(SQLModel, table=True):
    __tablename__ = "books"

    uid: uuid.UUID = Field(
        sa_column=Column(pg.UUID, default=uuid.uuid4, primary_key=True, nullable=False, unique=True)
    )
    user_id: Optional[uuid.UUID] = Field(default=None, foreign_key="users.uid")
    title: str = Field(sa_column=Column(pg.VARCHAR, nullable=False))
    author: str = Field(sa_column=Column(pg.VARCHAR, nullable=False))
    description: str = Field(sa_column=Column(pg.VARCHAR, nullable=False))
    price: int = Field(sa_column=Column(pg.INTEGER, nullable=False))
    created_at: datetime = Field(sa_column=Column(pg.TIMESTAMP, nullable=False, default=datetime.now))
    publisher: str = Field(sa_column=Column(pg.VARCHAR, nullable=False))
    page_count: int = Field(sa_column=Column(pg.INTEGER, nullable=False))
    updated_at: datetime = Field(sa_column=Column(pg.TIMESTAMP, nullable=False, default=datetime.now, onupdate=datetime.now))
    user: Optional["User"] = Relationship(back_populates="books")
    reviews: List["Review"] = Relationship(
        back_populates="book", sa_relationship_kwargs={"lazy": "selectin"}
    )
    tags: List["Tag"] = Relationship(
        link_model=BookTag,
        back_populates="books",
        sa_relationship_kwargs={"lazy": "selectin"},
    )

    def __repr__(self):
        return f"<Book {self.title}>"
    

class Review(SQLModel, table=True):
    __tablename__ = "reviews"

    uid: uuid.UUID = Field(
        sa_column=Column(pg.UUID, default=uuid.uuid4, primary_key=True, nullable=False, unique=True)
    )
    user_id: Optional[uuid.UUID] = Field(default=None, foreign_key="users.uid")
    book_uid: Optional[uuid.UUID] = Field(default=None, foreign_key="books.uid")
    review: str = Field(sa_column=Column(pg.VARCHAR, nullable=False))
    rating: int = Field(ge=1, le=5, sa_column=Column(pg.INTEGER, nullable=False))
    created_at: datetime = Field(sa_column=Column(pg.TIMESTAMP, default=datetime.now))
    updated_at: datetime = Field(sa_column=Column(pg.TIMESTAMP, default=datetime.now, onupdate=datetime.now))
    user: Optional[User] = Relationship(back_populates="reviews")
    book: Optional[Book] = Relationship(back_populates="reviews")

    def __repr__(self) -> str:
        return f"<Review for {self.book_uid} created by {self.user_id}>"
    
