from pathlib import Path

from fastapi_mail import FastMail, MessageSchema, ConnectionConfig, MessageType
from fastapi_mail.errors import ConnectionErrors
from pydantic import EmailStr
from src.conf.config import config

conf = ConnectionConfig(
    MAIL_USERNAME=config.SMTP_USER,
    MAIL_PASSWORD=config.SMTP_PASSWORD,
    MAIL_FROM=config.SMTP_FROM,
    MAIL_PORT=config.SMTP_PORT,
    MAIL_SERVER=config.SMTP_HOST,
    TEMPLATE_FOLDER=Path(__file__).parent.parent / "templates",
    VALIDATE_CERTS=True,
    USE_CREDENTIALS=True,
    MAIL_SSL_TLS=True,
    MAIL_STARTTLS=False,
    MAIL_FROM_NAME="REST API Service",
)


async def send_verification_email(email: EmailStr, access_token: str, user_info: dict):
    fullname = f"{user_info.name} {user_info.surname}"
    message = MessageSchema(
        subject="Verify your email",
        recipients=[email],
        template_body={
            "fullname": fullname,
            "verification_link": f"{config.API_URL}/auth/verify-email?token={access_token}",
        },
        subtype=MessageType.html,
    )
    fm = FastMail(conf)
    try:
        await fm.send_message(message, template_name="email_verification.html")
    except ConnectionErrors as e:
        print(f"Failed to send email: {e}")
