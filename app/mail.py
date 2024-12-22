from fastapi_mail import FastMail, MessageSchema, ConnectionConfig, MessageType
from app.DataBase.config import Config
from typing import List


mail_config = ConnectionConfig(
    MAIL_USERNAME=Config.MAIL_USERNAME,
    MAIL_PASSWORD=Config.MAIL_PASSWORD,
    MAIL_FROM=Config.MAIL_FROM,
    MAIL_PORT=Config.MAIL_PORT,
    MAIL_SERVER=Config.MAIL_SERVER,
    MAIL_FROM_NAME=Config.MAIL_FROM_NAME,
    MAIL_STARTTLS=True,  
    MAIL_SSL_TLS=False, 
    USE_CREDENTIALS=True,
    VALIDATE_CERTS=True,
)

mail = FastMail(mail_config)

def SendMail(recipients:List[str], subject:str, body:str):
    message = MessageSchema(
        recipients=recipients,
        subject=subject,
        body=body,
        subtype=MessageType.html
    )
    
    return message