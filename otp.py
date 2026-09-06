import os
import random
import smtplib

from email.message import EmailMessage
from dotenv import load_dotenv


load_dotenv()


GMAIL_ADDRESS = os.getenv("GMAIL_ADDRESS")
GMAIL_APP_PASSWORD = os.getenv("GMAIL_APP_PASSWORD")


def generate_otp():

    return str(random.randint(100000, 999999))


def send_otp(receiver_email, otp):

    if not GMAIL_ADDRESS:
        raise ValueError(
            "GMAIL_ADDRESS is missing from .env"
        )

    if not GMAIL_APP_PASSWORD:
        raise ValueError(
            "GMAIL_APP_PASSWORD is missing from .env"
        )

    message = EmailMessage()

    message["Subject"] = "ResumeAI - Email Verification OTP"
    message["From"] = GMAIL_ADDRESS
    message["To"] = receiver_email

    message.set_content(
        f"""
Hello,

Your ResumeAI verification OTP is:

{otp}

This OTP is valid for 5 minutes.

Please do not share this OTP with anyone.

Regards,
ResumeAI Team
"""
    )

    with smtplib.SMTP_SSL(
        "smtp.gmail.com",
        465
    ) as server:

        server.login(
            GMAIL_ADDRESS,
            GMAIL_APP_PASSWORD
        )

        server.send_message(message)