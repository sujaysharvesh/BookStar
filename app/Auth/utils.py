from passlib.context import CryptContext
from datetime import timedelta, datetime
import jwt
from app.DataBase.config import Config
import uuid
import logging
from itsdangerous import URLSafeTimedSerializer

password_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
access_token_expires = 3600  

def generate_password_hash(password: str):
    return password_context.hash(password)

def verify_password(password: str, hash: str) -> bool:
    return password_context.verify(password, hash)

def create_access_token(user_data: dict, expires_delta: timedelta | None = None, refresh: bool = False):
    payload = {
        "user": user_data,
        "exp": datetime.utcnow() + (expires_delta if expires_delta else timedelta(seconds=access_token_expires)),
        "jti": str(uuid.uuid4()),
        "refresh": refresh,
    }
    token = jwt.encode(
        payload=payload,
        key=Config.JWT_SECRET,
        algorithm=Config.JWT_ALGORITHM
    )
    return token

def decode_token(token: str):
    try:
        token_data = jwt.decode(
            token,
            key=Config.JWT_SECRET,
            algorithms=[Config.JWT_ALGORITHM]
        )
        return token_data
    except jwt.PyJWTError as e:
        logging.error(f"Error decoding token: {e}")
        return None

serializer = URLSafeTimedSerializer(Config.JWT_SECRET, salt="email-verifier")

def generate_confirmation_token(data:dict):
    return serializer.dumps(data)

def confirm_token(token:str, expiration=3600):
    try:
        data = serializer.loads(token, max_age=expiration)
    except Exception as e:
        logging.error(f"Error confirming token: {e}")
        return False
    return data 