from workers.celery_app import celery_app


@celery_app.task
def generate_production_report(batch_id: int):
    # Add actual database query and report generation here.
    return {
        "batch_id": batch_id,
        "status": "report_requested",
    }


import asyncio

from workers.celery_app import celery_app
from services.email_service import send_email


@celery_app.task(name="workers.tasks.send_alert_email")
def send_alert_email(
    to_email: str,
    subject: str,
    body: str,
):
    asyncio.run(
        send_email(to_email, subject, body)
    )
    return {"status": "sent"}