import os
import aiosmtplib

from email.message import EmailMessage


async def send_email(
    to_email: str,
    subject: str,
    body: str,
):
    message = EmailMessage()
    message["From"] = os.environ["EMAIL_FROM"]
    message["To"] = to_email
    message["Subject"] = subject
    message.set_content(body)

    await aiosmtplib.send(
        message,
        hostname=os.environ["SMTP_HOST"],
        port=int(os.getenv("SMTP_PORT", "587")),
        username=os.environ["SMTP_USERNAME"],
        password=os.environ["SMTP_PASSWORD"],
        start_tls=True,
        timeout=20,
    )