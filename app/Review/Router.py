from fastapi import APIRouter,Depends, HTTPException, status
from app.Auth.dependencies import get_current_user
from sqlalchemy.ext.asyncio.session import AsyncSession
from app.DataBase.main import get_session
from app.Review.Service import ReviewService
from .schema import ReviewCreateModel, ReviewUpdateMOdel
from app.Auth.dependencies import AccessTokenBearer, RoleChecker

review_router = APIRouter()
review_service = ReviewService()


admin_role_checker = RoleChecker(["admin"])
user_role_checker = RoleChecker(["user", "admin"])

@review_router.get('/')
async def GetAllReview(session: AsyncSession = Depends(get_session),
                       current_user: str = Depends(get_current_user),
                       _: bool = Depends(admin_role_checker)):
    reviews = await review_service.AllReview(session)
    return reviews

@review_router.post('/book/{book_id}')
async def AddReview(
                    book_id:str,
                    review_details:ReviewCreateModel,
                    current_user: str = Depends(get_current_user),
                    _: bool = Depends(user_role_checker),
                    session: AsyncSession = Depends(get_session)):
    
    new_review = await review_service.CreateReview(
        Book_id=book_id,
        user_email=current_user.email,
        session=session,
        review_data=review_details
    )
    return new_review

@review_router.get("/{book_id}")
async def getReview(book_id: str,
                    session: AsyncSession = Depends(get_session),
                    current_user: str = Depends(get_current_user),
                    _: bool = Depends(user_role_checker)):
    review = await review_service.GetReview(book_id, session)
    return review

@review_router.get('/book/{book_id}')
async def bookReviews(book_id: str, session: AsyncSession = Depends(get_session),
                      current_user: str = Depends(get_current_user),
                      _: bool = Depends(admin_role_checker)):
    reviews = await review_service.GetReviewsByBookID(book_id, session)
    return reviews

@review_router.patch('/{review_id}')
async def updateReview(review_id:str,
                       review_details:ReviewUpdateMOdel,
                       session: AsyncSession = Depends(get_session),
                       current_user: str = Depends(get_current_user),
                       _: bool = Depends(user_role_checker)):
    updatedReview = await review_service.UpdateReview(review_id, review_details, session)
    return updatedReview    

@review_router.delete('/{review_id}')
async def deleteReview(review_id: str,
                       session: AsyncSession = Depends(get_session),
                       current_user: str = Depends(get_current_user),
                       _: bool = Depends(user_role_checker)):
    
    review = await review_service.DeleteReview(review_id, session)
    if review:
        return "Review Deleted"
    else:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,detail="Book Not Found")
