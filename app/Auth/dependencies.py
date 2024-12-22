from typing import Any, Optional
from fastapi import HTTPException, status, Depends, Request
from fastapi.security import HTTPBearer
from app.DataBase.redis import token_in_blocklist
from .utils import decode_token
from app.Auth.service import UserService
from app.DataBase.main import get_session
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List, Any
from app.DataBase.models import User
from app.error import AccountNotVerified

User_service = UserService()


class TokenBearer(HTTPBearer):
    def __init__(self, *, bearerFormat: Optional[str] = None, scheme_name: Optional[str] = None, description: Optional[str] = None, auto_error: bool = True):
        super().__init__(bearerFormat=bearerFormat, scheme_name=scheme_name, description=description, auto_error=auto_error)

    async def __call__(self, request: Request):
        creds = await super().__call__(request)
        token = creds.credentials
        token_data = decode_token(token)
        if token_data is None:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Invalid token")
        if await token_in_blocklist(token_data["jti"]):

            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Token is in the blocklist")
        self.verify_token_data(token_data)
        return token_data

    def verify_token_data(self, token_data: dict) -> None:
        raise NotImplementedError("This method must be overridden by subclasses")


class AccessTokenBearer(TokenBearer):
    def verify_token_data(self, token_data: dict) -> None:
        if token_data.get('refresh'):
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Please provide an access token")


class RefreshTokenBearer(TokenBearer):
    def verify_token_data(self, token_data: dict) -> None:
        if not token_data.get('refresh'):
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Please provide a refresh token")

async def get_current_user(request: Request, token_details: dict = Depends(AccessTokenBearer()), session: AsyncSession = Depends(get_session)):
        user_email = token_details['user']['email']
        user = await User_service.get_user_by_email(user_email, session)
        return user
    
    
class RoleChecker:
    def __init__(self, allowed_roles: List[str]) -> None:
        self.allowed_roles = allowed_roles
        
        
    def __call__(self, current_user: User = Depends(get_current_user)) -> Any:
        if not current_user.is_verified:
            raise AccountNotVerified()
        if current_user.rol in self.allowed_roles:
            return True
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="You are Unautherised to perform this task")