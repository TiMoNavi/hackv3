import os
from fastapi_mail import FastMail, MessageSchema, ConnectionConfig
from app.core.config import settings
import logging


def _get_mail_conf() -> ConnectionConfig:

    return ConnectionConfig(
        MAIL_USERNAME=settings.MAIL_USERNAME,
        MAIL_PASSWORD=settings.MAIL_PASSWORD,
        MAIL_FROM=settings.MAIL_FROM,
        MAIL_FROM_NAME=settings.MAIL_FROM_NAME,
        MAIL_PORT=settings.MAIL_PORT,
        MAIL_SERVER=settings.MAIL_SERVER,
        MAIL_STARTTLS=settings.MAIL_STARTTLS,
        MAIL_SSL_TLS=settings.MAIL_SSL_TLS,
        USE_CREDENTIALS=bool(settings.MAIL_USERNAME),
        VALIDATE_CERTS=False
    )


logger = logging.getLogger(__name__)


async def send_verification_code(email: str, code: str):
    try:
        fm = FastMail(_get_mail_conf())
        message = MessageSchema(
            subject="Your verification code",
            recipients=[email],
            body=f"Your code: {code}",
            subtype="plain",
        )
        await fm.send_message(message)
    except Exception as e:
        logger.exception("send_verification_code failed: %s", e)

