from app.DataBase.models import User
from .schema import UserCreateModel
from .utils import generate_password_hash, verify_password
from sqlmodel.ext.asyncio.session import AsyncSession
from sqlmodel import select
from sqlalchemy.exc import IntegrityError
from fastapi import HTTPException

class UserService:
    async def create_user(self, user_details: UserCreateModel, session: AsyncSession):
        user_data = user_details.dict()
        user_data["password"] = generate_password_hash(user_data.pop("password"))
        user_data['rol'] = 'user'  
        new_user = User(**user_data)
        
        try:
            session.add(new_user)
            await session.commit()  
            await session.refresh(new_user) 
        except Exception as e:
            await session.rollback()
            raise HTTPException(status_code=500, detail="Failed to create user")
        
        return new_user
    
    async def get_user_by_email(self, email: str, session: AsyncSession):
        statement = select(User).where(User.email == email)
        result = await session.execute(statement)
        user = result.scalars().first()
        return user
    
    async def user_exists(self, email: str, session: AsyncSession):
        user = await self.get_user_by_email(email, session)
        return user is not None 
    
    async def update_user(self, user: User, user_data:dict, session: AsyncSession):
        for key, value in user_data.items():
            setattr(user, key, value)
        await session.commit()
        return user
    
    async def delete_user(self, email: str, session: AsyncSession):
        user = await self.get_user_by_email(email, session)
        await session.delete(user)
        await session.commit()
        return None 