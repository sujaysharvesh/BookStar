from app.DataBase.models import Review
from sqlmodel.ext.asyncio.session import AsyncSession
from app.DataBase.main import get_session
from .schema import ReviewCreateModel, ReviewUpdateMOdel
from fastapi.exceptions import HTTPException
from fastapi import status
from app.Auth.service import UserService
from app.Books.service import BookService
import logging
from sqlmodel import select
from app.Auth.dependencies import AccessTokenBearer, RoleChecker

user_service = UserService()
book_service = BookService()

class ReviewService:
    async def CreateReview(self, Book_id: str,user_email:str, session: AsyncSession, review_data: ReviewCreateModel):
        try:
            book = await book_service.get_book(Book_id, session)
            user = await user_service.get_user_by_email(user_email, session)
            if not book:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="Book not found"
                )
            if not user:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="User not found"
                )
            new_review = Review(**review_data.dict(), user=user, book=book)
            session.add(new_review)
            await session.commit()
            await session.refresh(new_review)
            return new_review
             
        except Exception as e:
            logging.error(f"Error creating review: {str(e)}")
            raise HTTPException(
                status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Oobs something went wrong"
            )
    
    async def AllReview(self, session: AsyncSession):
        statement = select(Review).order_by(Review.created_at.desc())
        result = await session.execute(statement)
        return result.scalars().all()
    
    async def GetReview(self, review_id: str, session: AsyncSession):
        statement = select(Review).where(Review.uid == review_id)
        result = await session.execute(statement)
        return result.scalars().first()
    
    async def GetReviewsByBookID(self, book_id:str, session: AsyncSession):
        statement = select(Review).where(Review.book_uid == book_id).order_by(Review.created_at.desc())
        result = await session.execute(statement)
        return result.scalars().all()
    
    async def DeleteReview(self, review_id: str, session: AsyncSession):
        review = await self.GetReview(review_id, session)
        if review:
            await session.delete(review)
            await session.commit()
            return True
        return False
    
    async def UpdateReview(self, review_id: str, reviewDetail: ReviewUpdateMOdel, session: AsyncSession):
        review = await self.GetReview(review_id, session)
        if review:
            for key, values in reviewDetail.dict(exclude_unset=True).items():
                setattr(review, key, values)
                
            session.add(review)
            await session.commit()
            await session.refresh(review)
            return review
        else:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Review Not Found")