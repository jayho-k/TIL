from app.core.celery_app import celery_app

@celery_app.task(name="send_welcome_email")
def send_welcome_email(email: str):
    # Simulate heavy task
    print(f"Sending welcome email to {email}...") 
    return f"Email sent to {email}"
