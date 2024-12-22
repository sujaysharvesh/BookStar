from sqlmodel.ext.asyncio.session import AsyncSession
from app.DataBase.models import Book
from sqlmodel import select
from app.Books.schema import BookCreateModel, BookUpdateModel

class BookService:
    async def get_all_books(self, Session: AsyncSession):
        statement = select(Book).order_by(Book.created_at.desc())
        result = await Session.execute(statement)
        return result.scalars().all()  
    
    async def get_user_books(self,user_uid:str, Session: AsyncSession):
        statement = select(Book).where(Book.user_id == user_uid).order_by(Book.created_at.desc())
        result = await Session.execute(statement)
        return result.scalars().all()
    
    async def get_book(self, book_uid: str, Session: AsyncSession):
        statement = select(Book).where(Book.uid == book_uid)
        result = await Session.execute(statement)
        return result.scalars().first() 

    async def create_book(self, book_data: BookCreateModel, user_uid:str, Session: AsyncSession):
        new_book = Book(**book_data.dict())
        new_book.user_id = user_uid  
        Session.add(new_book)  
        await Session.commit()  
        await Session.refresh(new_book)  
        return new_book
    
    async def Update_book(self, book_uid: str, book_data: BookUpdateModel, Session: AsyncSession):
        book_to_update = await self.get_book(book_uid, Session)
        if book_to_update:
            for key, value in book_data.dict(exclude_unset=True).items():
                setattr(book_to_update, key, value)
            
            await Session.commit()  
            await Session.refresh(book_to_update)  
            return book_to_update
        else:
            return None

    async def Delete_book(self, book_uid: str, Session: AsyncSession):
        book_to_delete = await self.get_book(book_uid, Session)
        
        if book_to_delete:
            await Session.delete(book_to_delete)  
            await Session.commit()  
            return True
        return False
