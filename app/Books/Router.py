from fastapi import APIRouter, Depends, HTTPException, status
from sqlmodel.ext.asyncio.session import AsyncSession
from typing import List
from app.DataBase.models import Book
from app.DataBase.main import get_session
from app.Books.service import BookService
from app.Auth.dependencies import AccessTokenBearer, RoleChecker
from .schema import BookDeltailModel

router = APIRouter()
book_service = BookService()
access_token = AccessTokenBearer()
role_checker = RoleChecker(['admin','user'])

@router.get("/", response_model=List[Book])
async def get_all_books(session: AsyncSession = Depends(get_session), token_details= Depends(access_token), _:bool = Depends(role_checker)) -> dict:
    books = await book_service.get_all_books(session)
    return books

@router.get("/user_books", response_model=List[Book])
async def get_user_book(session: AsyncSession = Depends(get_session), token_details= Depends(access_token), _:bool = Depends(role_checker)) -> dict:
    user_uid = token_details['user']['user_uid']
    books = await book_service.get_user_books(user_uid, session)
    return books

@router.post("/", status_code=status.HTTP_201_CREATED, response_model=Book)
async def create_book(book: Book, session: AsyncSession = Depends(get_session), token_details= Depends(access_token), _:bool = Depends(role_checker)) -> dict:
    user_uid = token_details['user']['user_uid']
    new_book = await book_service.create_book(book, user_uid, session)
    return new_book

@router.get("/{book_uid}", response_model=BookDeltailModel)
async def get_book(book_uid: str, session: AsyncSession = Depends(get_session), token_details= Depends(access_token), _:bool = Depends(role_checker)) -> dict:
    book = await book_service.get_book(book_uid, session)
    if book:
        return book  
    else:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Book not found")

@router.patch("/{book_uid}", response_model=Book)
async def update_book(book_uid: str, book: Book, session: AsyncSession = Depends(get_session), token_details= Depends(access_token), _:bool = Depends(role_checker))-> dict:
    updated_book = await book_service.Update_book(book_uid, book, session)  
    if updated_book:
        return updated_book
    else:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Book not found")

@router.delete("/{book_uid}")
async def delete_book(book_uid: str, session: AsyncSession = Depends(get_session), token_details= Depends(access_token), _:bool = Depends(role_checker)):
    book = await book_service.Delete_book(book_uid, session)  
    if book:
        return None  
    else:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Book not found")
