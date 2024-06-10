from fastapi import APIRouter, Depends, HTTPException, Request
from sqlalchemy.orm import Session

from app.models.news import News
from app.models.user import SignupUser, LoginUser, UserDB, UserInDB, ChangePasswordRequest, FullNameUpdate, UsernameUpdate, Post, PostCreate, PostInDB, CommentCreate, Comment, CommentInDB
from app.models.auth import Token
from app.database import SessionLocal
from app.routers.user.security import create_access_token, get_password_hash, verify_password, \
    generate_verification_token, get_current_user
import smtplib
from email.mime.text import MIMEText
from fastapi.templating import Jinja2Templates
from app.scrapers.standings.standing import get_club_names_from_leagues
from app.database import get_db
from fastapi.security import OAuth2PasswordBearer
from fastapi.responses import JSONResponse
from typing import List

router = APIRouter()

templates = Jinja2Templates(directory="templates")


# Dependency to get a database session


@router.post("/register/", response_model=UserInDB)
def register_user(user: SignupUser, db: Session = Depends(get_db)):
    if user.email is None:
        raise HTTPException(status_code=400, detail="Email is required for registration")

    db_user = db.query(UserDB).filter(UserDB.username == user.username).first()
    if db_user:
        raise HTTPException(status_code=400, detail="Username already registered")

    hashed_password = get_password_hash(user.password)

    user_dict = user.dict(exclude={"password"})
    if user.full_name:
        user_dict["full_name"] = user.full_name
    if user.favorite_team:
        user_dict["favorite_team"] = user.favorite_team

    verification_token = generate_verification_token()
    user_db = UserDB(**user_dict, password=hashed_password, verification_token=verification_token, is_verified=False)

    db.add(user_db)
    db.commit()
    db.refresh(user_db)

    # Send the email with the verification link
    send_email(user.email, verification_token)

    return user_db


def send_email(email: str, verification_token: str):
    # Construct the verification link
    verification_link = f"http://localhost:8080/api/verify-email/?token={verification_token}"

    smtp_server = "smtp.gmail.com"
    smtp_port = 587
    smtp_username = "teampython91@gmail.com"
    smtp_password = "seke onpu smgf aqem"

    msg = MIMEText(f"Click the following link to verify your email: {verification_link}")
    msg["Subject"] = "Email Verification"
    msg["From"] = "teampython91@gmail.com"
    msg["To"] = email

    try:
        with smtplib.SMTP(smtp_server, smtp_port) as server:
            server.starttls()
            server.login(smtp_username, smtp_password)
            server.sendmail("teampython91@gmail.com", [email], msg.as_string())
    except Exception as e:
        # Handle email sending errors here
        print("Email sending error:", str(e))


@router.post("/login/", response_model=Token)
def login_user(user_credentials: LoginUser, db: Session = Depends(get_db)):
    username = user_credentials.username
    password = user_credentials.password

    db_user = db.query(UserDB).filter(UserDB.username == username).first()
    if db_user is None or not verify_password(password, db_user.password):
        raise HTTPException(status_code=401, detail="Incorrect username or password")

    access_token = create_access_token(data={"sub": db_user.username})
    return {"access_token": access_token, "token_type": "bearer"}


@router.get('/verify-email/')
def verify_email(token: str,request: Request, db: Session = Depends(get_db)):
    user = db.query(UserDB).filter(UserDB.verification_token == token).first()
    if user:
        user.is_verified = True
        user.verification_token = None  # Clear the token after verification
        db.commit()
        return templates.TemplateResponse("verification.html", {"request": request})  # You can customize this response
    else:
        return templates.TemplateResponse("error.html", {"request": request})


@router.get('/view')
async def login_view(request: Request):
    db: Session = SessionLocal()
    hg = db.query(UserDB).all()
    return templates.TemplateResponse('auth.html', {'request': request, 'hg': hg})

@router.get("/club-names/")
def get_club_names():
    club_names = get_club_names_from_leagues()
    return {"club_names": club_names}


@router.post("/change-password/")
def change_password(request: Request, change_password_data: ChangePasswordRequest, db: Session = Depends(get_db), current_user: UserDB = Depends(get_current_user)):
    # Verify the old password
    if not verify_password(change_password_data.old_password, current_user.password):
        raise HTTPException(status_code=400, detail="Incorrect old password")

    # Hash the new password
    new_password_hash = get_password_hash(change_password_data.new_password)

    # Update the user's password
    current_user.password = new_password_hash
    db.commit()

    return {"message": "Password changed successfully"}

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")
@router.post("/logout")
def logout_user(token: str = Depends(oauth2_scheme)):
    response = JSONResponse(content={"message": "Logout successful"})
    response.delete_cookie("access_token")

    return response

@router.get("/forgot-password/")
async def forgot_password_view(request: Request):
    return templates.TemplateResponse("forgot_password.html", {"request": request})


@router.get("/profile/")
async def profile_view(request: Request):
    return templates.TemplateResponse("profile.html", {"request": request})

# @router.get("/blog/")
# async def blog_view(request: Request):
#     db = SessionLocal()
#     news = db.query(News).all()
#     return templates.TemplateResponse("social.html", {"request": request, "news": news})


@router.get("/user-profile")
def get_user_profile(user: UserDB = Depends(get_current_user)):
    user_profile = {
        "full_name": user.full_name,
        "username": user.username,
        "email": user.email,
        "favorite_team": user.favorite_team,
        "created_at": user.created_at,
        "is_verified": user.is_verified
        # Add more fields as needed
    }

    return user_profile

@router.put("/change-fullname/")
def change_full_name(user_update: FullNameUpdate, db: Session = Depends(get_db), current_user: UserDB = Depends(get_current_user)):
    current_user.full_name = user_update.full_name
    db.commit()
    return {"message": "Full name updated successfully"}


@router.put("/change-username/")
def change_username(username_update: UsernameUpdate, db: Session = Depends(get_db), current_user: UserDB = Depends(get_current_user)):
    new_username = username_update.username

    # Check if the new username is already taken
    existing_user = db.query(UserDB).filter(UserDB.username == new_username).first()
    if existing_user:
        raise HTTPException(status_code=400, detail="Username already in use")

    current_user.username = new_username
    db.commit()
    return {"message": "Username updated successfully"}

@router.post("/create-post/", response_model=PostInDB)
def create_post(post: PostCreate, current_user: UserDB = Depends(get_current_user), db: Session = Depends(get_db)):
    post_db = Post(**post.dict(), user_id=current_user.id)
    db.add(post_db)
    db.commit()
    db.refresh(post_db)
    return post_db

@router.post("/create-comment/{post_id}", response_model=CommentInDB)
def create_comment(post_id: int, comment: CommentCreate, current_user: UserDB = Depends(get_current_user), db: Session = Depends(get_db)):
    post = db.query(Post).filter(Post.id == post_id).first()
    if not post:
        raise HTTPException(status_code=404, detail="Post not found")

    comment_db = Comment(**comment.dict(), user_id=current_user.id, post_id=post_id)
    db.add(comment_db)
    db.commit()
    db.refresh(comment_db)
    return comment_db

@router.get("/user-posts/{user_id}", response_model=List[PostInDB])
def get_user_posts(user_id: int, db: Session = Depends(get_db)):
    posts = db.query(Post).filter(Post.user_id == user_id).all()
    if not posts:
        raise HTTPException(status_code=404, detail="User has no posts")
    return posts

@router.get("/user-comments/{user_id}", response_model=List[CommentInDB])
def get_user_comments(user_id: int, db: Session = Depends(get_db)):
    comments = db.query(Comment).filter(Comment.user_id == user_id).all()
    if not comments:
        raise HTTPException(status_code=404, detail="User has no comments")
    return comments

@router.get("/post-comments/{post_id}", response_model=List[CommentInDB])
def get_post_comments(post_id: int, db: Session = Depends(get_db)):
    comments = db.query(Comment).filter(Comment.post_id == post_id).all()
    if not comments:
        raise HTTPException(status_code=404, detail="Post has no comments")
    return comments

@router.get("/posts-by-criteria/")
def get_posts_by_criteria(criteria: str, db: Session = Depends(get_db)):
    posts = db.query(Post).filter(Post.content.contains(criteria)).all()
    if not posts:
        raise HTTPException(status_code=404, detail="No posts match the criteria")
    return posts

@router.get("/all-posts/", response_model=List[PostInDB])
def get_all_posts(db: Session = Depends(get_db)):
    posts = db.query(Post).all()
    return posts


@router.get("/user-profile/{user_id}", response_model=SignupUser)
def get_user_profile_by_id(user_id: int, db: Session = Depends(get_db)):
    user = db.query(UserDB).filter(UserDB.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return user

