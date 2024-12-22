from fastapi import APIRouter, Depends, status, Request, BackgroundTasks
from .schema import ( UserCreateModel,
                     UserLoginModel,
                     UserBookModel,
                     MailModel,
                     DeleteAccountModel,
                     PasswordResetConfirmModel,
                     PasswordResetModel)
from sqlalchemy.ext.asyncio.session import AsyncSession
from app.DataBase.main import get_session
from .service import UserService
from fastapi.exceptions import HTTPException
from .utils import (create_access_token,
                    generate_password_hash,
                    verify_password,
                    generate_confirmation_token,
                    confirm_token)
from fastapi.responses import JSONResponse
from datetime import timedelta, datetime
from .dependencies import (AccessTokenBearer,
                           RefreshTokenBearer,
                           get_current_user,
                           RoleChecker)
from app.DataBase.redis import add_jti_to_blocklist, token_in_blocklist
from app.mail import SendMail, mail
from app.error import UserAlreadyExists, UserNotFound
from app.DataBase.config import Config
from app.celeryTask import send_email

Auth_router = APIRouter()
User_service = UserService()
access_token_bearar = AccessTokenBearer()
role_checker = RoleChecker(['admin', 'user'])

@Auth_router.post('/send_mail', status_code=status.HTTP_200_OK)
async def sendMail(Email: MailModel):
    recipients = [Email.address] 
    subject = "Test Mail"  
    body = "<h1>Test Mail</h1>" 
    send_email.delay(recipients, subject, body)
    return JSONResponse(content={"message": "Mail Sent Successfully"})


@Auth_router.post('/signup', status_code=status.HTTP_201_CREATED)
async def create_user(user_details: UserCreateModel,bg_task: BackgroundTasks, session: AsyncSession = Depends(get_session)):
    email = user_details.email
    user_exists = await User_service.user_exists(email, session)
    if user_exists:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="User with this email already exists."
        )  
    new_user = await User_service.create_user(user_details, session)
    token = generate_confirmation_token({"email": email})
    link = f"http://{Config.DOMAIN}/api/v1/Auth/verify/{token}"
    html_message = f"""
    <h1>Click the link below to verify your email</h1>
    <a href="{link}">Verify Email</a>
    """   
    try:
        mail_message = SendMail(
            recipient=[email],
            subject="Email Verification",
            body=html_message
        )
        bg_task.add_task(mail.send_message,mail_message)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Account created, but failed to send verification email. Please try again later."
        )
    return  { "message": "User Created Successfully Check your email for verification link", 
             "user": new_user} 

@Auth_router.get('/verify/{token}', status_code=status.HTTP_200_OK)
async def verify_email(token: str, session: AsyncSession = Depends(get_session)):
    token_data = confirm_token(token)
    user_email = token_data.get("email")
    if user_email:
        user = await User_service.get_user_by_email(user_email, session)
        if not user:
            UserNotFound()
        await User_service.update_user(user, {"is_verified": True}, session)
        return JSONResponse(status_code=status.HTTP_200_OK,
                            content={"message": "Email Verified Successfully"})
    raise HTTPException(
        status_code=status.HTTP_400_BAD_REQUEST,
        detail="Error occurred while verifying email. Please try again."
    )

@Auth_router.post('/login', status_code=status.HTTP_200_OK)
async def login(user_data: UserLoginModel, session: AsyncSession = Depends(get_session)):
    email = user_data.email
    password = user_data.password

    user = await User_service.get_user_by_email(email, session)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid Credentials"
        )

    if not verify_password(password, user.password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid Credentials"
        )
        
    access_token = create_access_token(
        user_data={
            "email": user.email,
            "user_uid": str(user.uid),
            "role": user.rol
        }
    )
    refresh_token = create_access_token(
        user_data={
            "email": user.email,
            "user_uid": str(user.uid),
        },
        refresh=True,
        expires_delta=timedelta(days=2)
    )
    
    return {
        "message": "Login Successful",
        "access_token": access_token,
        "refresh_token": refresh_token,
        "user": {
            "email": user.email,
            "username": user.username,
            "user_uid": str(user.uid)
        }
    }
    
@Auth_router.get("/refresh_token")
async def create_new_acces_token(token_details: dict = Depends(RefreshTokenBearer())):
    expiry_timestamp = token_details['exp']
    
    if datetime.fromtimestamp(expiry_timestamp) > datetime.now():
        new_access_token = create_access_token(user_data=token_details['user'])
        return JSONResponse(content={"Access Token": new_access_token})
    
    raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid or Expired Token")


@Auth_router.get("/me", response_model=UserBookModel)
async def get_current_user(user_details: dict = Depends(get_current_user), _: bool = Depends(role_checker)):
    return user_details


@Auth_router.get("/logout")
async def revoke_token(token_details: dict = Depends(AccessTokenBearer())):
    jti = token_details["jti"]

    await add_jti_to_blocklist(jti)

    return JSONResponse(
        content={"message": "Logged Out Successfully"}, status_code=status.HTTP_200_OK
    )

@Auth_router.delete('/delete', status_code=status.HTTP_200_OK)
async def DeleteAccount(user_data: DeleteAccountModel, session: AsyncSession = Depends(get_session)):
    email = user_data.email
    password = user_data.password

    user = await User_service.get_user_by_email(email, session)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid Credentials"
        )

    if not verify_password(password, user.password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid Credentials"
        )
    await User_service.delete_user(email, session)
    return JSONResponse(content={"message": "Account Deleted Successfully"}, status_code=status.HTTP_200_OK)

@Auth_router.post("/password-reset-request", status_code=status.HTTP_200_OK)
async def password_reset_request(email: PasswordResetModel, session: AsyncSession = Depends(get_session)):
    email = await User_service.get_user_by_email(email.email, session)
    if not email:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    token = generate_confirmation_token({"email": email.email})
    link = f"http://{Config.DOMAIN}/api/v1/Auth/password-conf/{token}"
    html_message = f"""
    <h1>Click the link below to reset your password</h1>
    <a href="{link}">Reset Password</a>
    """
    try:
        mail_message = SendMail(
            recipient=[email.email],
            subject="Password Reset",
            body=html_message
        )
        await mail.send_message(mail_message)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to send password reset email. Please try again later."
        )
    return JSONResponse(content={"message": "Password reset link sent successfully"})

@Auth_router.post("/password-conf/{token}", status_code=status.HTTP_200_OK)
async def password_reser_confirm(token: str,
                                 password_data: PasswordResetConfirmModel,
                                 session: AsyncSession = Depends(get_session)):
    token_data = confirm_token(token)
    user_email = token_data.get("email")
    new_password = password_data.new_password
    confirm_password = password_data.confirm_password
    if new_password != confirm_password:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Passwords do not match"
        )
    if user_email:
        user = await User_service.get_user_by_email(user_email, session)
        if not user:
            UserNotFound()
        new_password = generate_password_hash(new_password)
        await User_service.update_user(user, {"password": new_password}, session)
        return JSONResponse(status_code=status.HTTP_200_OK,
                            content={"message": "Password Reset Successfully"})
    raise HTTPException(
        status_code=status.HTTP_400_BAD_REQUEST,
        detail="Error occurred while resetting password. Please try again."
    )