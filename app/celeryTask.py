from celery import Celery
from app.mail import mail, SendMail
from asgiref.sync import async_to_sync

app = Celery()

app.config_from_object("app.DataBase.config")
app.conf.update(
    worker_concurrency=1, 
    pool='prefork', 
)


@app.task()
def send_email(recipients: list[str], subject: str, body: str):

    message = SendMail(recipients=recipients, subject=subject, body=body)

    async_to_sync(mail.send_message)(message)
    print("Email sent")