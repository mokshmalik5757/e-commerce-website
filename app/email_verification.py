from dotenv import load_dotenv
load_dotenv()
from fastapi_mail import FastMail, MessageSchema, ConnectionConfig, MessageType
import os
from app.schemas import Signup
from app.token import create_access_token
from jinja2 import Environment, FileSystemLoader

env = Environment(loader=FileSystemLoader('./app/templates'))
email_template = env.get_template('email_template.html')

conf = ConnectionConfig(
    MAIL_USERNAME =os.environ["MAIL_USERNAME"],
    MAIL_PASSWORD = os.environ["MAIL_PASSWORD"],
    MAIL_FROM = os.environ["MAIL_FROM"],
    MAIL_PORT = 465,
    MAIL_SERVER = "smtp.gmail.com",
    MAIL_STARTTLS = False,
    MAIL_SSL_TLS = True,
    USE_CREDENTIALS = True,
    VALIDATE_CERTS = True
)

async def send_email(email: list, instance: Signup):
    token_data = {
       "sub":instance.UserName}
    token = create_access_token(data=token_data)
    
    rendered_template = email_template.render(token = token)
      
    message=MessageSchema(
        subject="Account Verification Email",
        recipients=email, 
        body=rendered_template,
        subtype=MessageType.html
    )
    
    fm = FastMail(config=conf)
    
    await fm.send_message(message=message)