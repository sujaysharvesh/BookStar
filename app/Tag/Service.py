from fastapi import status
from app.Books.service import BookService
from sqlmodel.ext.asyncio.session import AsyncSession
from sqlmodel import select
from app.DataBase.models import Tag
from .schema import TagCreateModel, TagAddModel, TagModel
from fastapi import HTTPException


Book_service = BookService()

class TagService:
    async def getAllTags(self, session:AsyncSession):
        statement = select(Tag).order_by(Tag.created_at)
        result = await session.execute(statement)
        return result
        
    async def AddTagToBook(self, book_id:str, tag_data:TagAddModel, session:AsyncSession):
        book = await Book_service.get_book(book_id, session)
        if not book:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,detail="Book not found")
        for tag_items in tag_data.tags:
            result = await session.execute(select(Tag).where(Tag.name == tag_items.name))
            tag = result.one_or_none()
            if not tag:
                tag = Tag(tag_items.name)
            
            book.tags.append(tag)
            
        session.add(book)
        await session.commit()
        await session.refresh(book)
        return book
    
    async def get_tag_by_uid(self, tag_uid: str, session: AsyncSession):
        statement = select(Tag).where(Tag.uid == tag_uid)
        result = await session.exec(statement)
        return result.first()

    async def add_tag(self, tag_data: TagCreateModel, session: AsyncSession):
        statement = select(Tag).where(Tag.name == tag_data.name)
        result = await session.exec(statement)
        tag = result.first()

        if tag:
            raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Tag Already exists")
        new_tag = Tag(name=tag_data.name)

        session.add(new_tag)

        await session.commit()

        return new_tag

    async def update_tag(self, tag_uid, tag_update_data: TagCreateModel, session: AsyncSession):
        tag = await self.get_tag_by_uid(tag_uid, session)
        if not tag:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND)
        update_data_dict = tag_update_data.model_dump()
        for k, v in update_data_dict.items():
            setattr(tag, k, v)

            await session.commit()

            await session.refresh(tag)

        return tag

    async def delete_tag(self, tag_uid: str, session: AsyncSession):
        tag = self.get_tag_by_uid(tag_uid,session)
        if not tag:
            raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Tag Already exists")
        await session.delete(tag)
        await session.commit()