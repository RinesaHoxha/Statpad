import smtplib
from email.mime.text import MIMEText
from fastapi import APIRouter, Request, Form, HTTPException
from fastapi.templating import Jinja2Templates
from app.models.news import News
from app.database import SessionLocal

router = APIRouter(
    prefix='/contact',
    tags=['contact']
)
templates=Jinja2Templates(directory='templates')
@router.get("/contactform")
def contact(request: Request):
    db=SessionLocal()
    news = db.query(News).all()
    return templates.TemplateResponse("contact.html", {"request": request,'news':news})


@router.post("/submit")
def submit(request:Request,name: str = Form(), emailAddress: str = Form(), message: str = Form()):
    db=SessionLocal()
    print(name)
    print(emailAddress)
    print(message)
    error_details = None  # Initialize the error_details variable
    success_message = None  # Initialize the success_message variable

    try:
        # Your existing code for printing values
        print(name)
        print(emailAddress)
        print(message)

        # Validation
        if len(name) < 3:
            raise HTTPException(status_code=400, detail="Name must be at least 3 characters")

    #
    #     smtp_server = "smtp.gmail.com"
    #     smtp_port = 587
    #     smtp_username = "teampython@gmail.com"
    #     smtp_password = "iqvb jxsa asuo txvx"
    #
    #     email_content = f"Name: {name}\nEmail: {emailAddress}\nMessage: {message}"
    #
    #     msg = MIMEText(email_content)
    #     msg["Subject"] = "Form Submission"
    #     msg["From"] = emailAddress
    #     msg["To"] = 'teampython@gmail.com'
    #
    #     with smtplib.SMTP(smtp_server, smtp_port) as server:
    #         server.starttls()
    #         server.login(smtp_username, smtp_password)
    #         server.sendmail(emailAddress, 'teampython@gmail.com', msg.as_string())
    #
    #     # If the email is sent successfully, set the success message
        success_message = "Submit form successfully"
    except HTTPException as e:
        # Capture the error details
        error_details = {"status_code": e.status_code, "detail": e.detail}

    news = db.query(News).all()

    return templates.TemplateResponse(
        "contact.html",
        {"request": request, 'news': news, 'error_details': error_details, 'success_message': success_message}
    )