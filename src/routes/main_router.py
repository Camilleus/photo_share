from datetime import datetime

from fastapi import Request, HTTPException, APIRouter, Form, UploadFile, File
from fastapi.params import Depends
from sqlalchemy.orm import Session
from starlette import status
from starlette.responses import HTMLResponse, RedirectResponse, Response
from starlette.templating import Jinja2Templates

from src.database.db import get_db
from src.database.models import User, Picture, Comment
from src.services.auth import auth_service
import src.repository.pictures as picture_repository
import src.repository.comments as comment_repository
from src.conf.cloudinary import configure_cloudinary, generate_random_string
from src.services.qr import generate_qr_and_upload_to_cloudinary
import cloudinary
import cloudinary.uploader

templates = Jinja2Templates(directory='templates')
router = APIRouter()


@router.get("/", response_class=HTMLResponse)
async def index(request: Request,
                db: Session = Depends(get_db),
                current_user: User = Depends(auth_service.get_current_user_optional)
                ):

    if current_user is None:
        return RedirectResponse(url='/login', status_code=status.HTTP_302_FOUND)

    user = db.query(User).filter(User.id == current_user.id).first()
    pictures = db.query(Picture).all()

    context = {'request': request, 'user': user, 'pictures': pictures}
    return templates.TemplateResponse('home.html', context)


@router.get('/users')
async def users(request: Request,
                db: Session = Depends(get_db),
                current_user: User = Depends(auth_service.get_current_user_optional),
                ):

    if current_user is None or not current_user.admin:
        return RedirectResponse(url='/login', status_code=status.HTTP_401_UNAUTHORIZED)

    if current_user:
        user = db.query(User).filter(User.id == current_user.id).first()
        if user.admin:
            users_details = db.query(User).all()
            context = {'request': request, 'user': user, 'users_details': users_details}
            return templates.TemplateResponse('users.html', context)

    return RedirectResponse(url='/', status_code=status.HTTP_401_UNAUTHORIZED)


@router.get("/users/{user_id}")
async def show_user(request: Request,
                    user_id: int,
                    db: Session = Depends(get_db),
                    current_user: User = Depends(auth_service.get_current_user_optional)
                    ):

    user = db.query(User).filter(User.id == user_id).first()
    context = {"request": request, "user": user, 'current_user': current_user}

    return templates.TemplateResponse("user_details.html", context)


@router.post("/users/toggle-ban/{user_id}", response_class=HTMLResponse)
async def toggle_ban_user_by_admin(user_id: int,
                                   db: Session = Depends(get_db),
                                   current_user: User = Depends(auth_service.get_current_user_optional)
                                   ):
    if not current_user or not current_user.admin:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN,
                            detail="You do not have permission to perform this action.")

    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found.")

    # Toggle the ban status
    user.ban_status = not user.ban_status
    db.commit()

    return RedirectResponse(url="/users", status_code=status.HTTP_303_SEE_OTHER)


@router.post("/users/delete/{user_id}")
async def delete_user(user_id: int,
                      db: Session = Depends(get_db),
                      current_user: User = Depends(auth_service.get_current_user_optional)
                      ):

    if not current_user:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Authentication required.")

    # Check if the current user is trying to delete their own account or is an admin
    if current_user.id != user_id and not current_user.admin:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN,
                            detail="You do not have permission to perform this action.")

    user_to_delete = db.query(User).filter(User.id == user_id).first()
    if not user_to_delete:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found.")

    db.delete(user_to_delete)
    db.commit()

    if current_user.admin:
        return RedirectResponse(url="/users", status_code=status.HTTP_303_SEE_OTHER)

    return RedirectResponse(url="/", status_code=status.HTTP_303_SEE_OTHER)


async def picture_uploader(picture_url: str,
                           picture_json: dict,
                           user: User, qr: str,
                           description: str,
                           db: Session
                           ) -> Picture:

    picture = Picture(
        picture_url=picture_url,
        picture_json=picture_json,
        user_id=user.id,
        qr_code_picture=qr,
        description=description,
        created_at=datetime.now()
    )
    db.add(picture)
    db.commit()
    db.refresh(picture)
    return picture


@router.get("/picture/upload", response_class=HTMLResponse)
async def authentication_page(request: Request):
    return templates.TemplateResponse('picture_upload.html', {"request": request})


@router.post("/picture/upload", response_class=HTMLResponse)
async def upload_picture(request: Request,
                         picture: UploadFile = File(...),
                         description: str = Form(...),
                         metadata: str = Form("{}"),
                         qr_code: UploadFile = File(None),
                         current_user: User = Depends(auth_service.get_current_user_optional),
                         db: Session = Depends(get_db)
                         ):

    if not current_user:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Authentication required.")

    configure_cloudinary()
    picture_name = generate_random_string()
    picture = cloudinary.uploader.upload(picture.file, public_id=picture_name, folder='picture', overwrite=True)
    version = picture.get('version')

    picture_url = cloudinary.CloudinaryImage(picture['public_id']).build_url(version=version)
    qr = await generate_qr_and_upload_to_cloudinary(picture_url, picture)

    uploaded_picture = await picture_uploader(picture_url=picture_url,
                                              picture_json=picture,
                                              user=current_user,
                                              description=description,
                                              qr=qr,
                                              db=db)

    return RedirectResponse(url=f"/picture/{uploaded_picture.id}", status_code=status.HTTP_303_SEE_OTHER)


@router.get("/picture/{picture_id}", response_class=HTMLResponse)
async def get_picture(request: Request,
                      picture_id: int,
                      db: Session = Depends(get_db),
                      current_user: User = Depends(auth_service.get_current_user_optional)
                      ):

    if not current_user:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Authentication required.")

    picture = await picture_repository.get_one_picture(picture_id=picture_id, db=db)
    username_uploader = db.query(User.username).join(Picture, Picture.user_id == User.id).filter(Picture.id == picture_id).first()[0]
    comments = db.query(Comment.content,
                        User.username,
                        Comment.id,
                        Comment.user_id,
    ).join(User).filter(Comment.picture_id == picture_id).order_by(Comment.id.desc()).all()

    if not picture:
        raise HTTPException(status_code=status.HTTP_204_NO_CONTENT)

    context = {'request': request, 'picture': picture, 'user': current_user, 'comments': comments, 'username_uploader': username_uploader}
    return templates.TemplateResponse('picture.html', context)


@router.post("/picture/comments/add")
async def add_comment(picture_id: int = Form(...),
                      content: str = Form(...),
                      db: Session = Depends(get_db),
                      current_user: User = Depends(auth_service.get_current_user_optional)
                      ):

    if not current_user:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Authentication required.")

    picture = db.query(Picture).filter(Picture.id == picture_id).first()
    if not picture:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Picture not found.")

    comment = Comment(user_id=current_user.id,
                      content=content,
                      picture=picture,
                      created_at=datetime.now())

    db.add(comment)
    db.commit()
    db.refresh(comment)
    return RedirectResponse(url=f"/picture/{picture_id}", status_code=status.HTTP_303_SEE_OTHER)


@router.get("/comment/edit/{comment_id}", response_class=HTMLResponse)
async def edit_comment_form(request: Request,
                            comment_id: int,
                            db: Session = Depends(get_db),
                            current_user: User = Depends(auth_service.get_current_user_optional)
                            ):

    if not current_user:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="You must be logged in to edit comments.")

    comment = db.query(Comment).filter(Comment.id == comment_id).first()

    if not comment or comment.user_id != current_user.id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="You can only edit your own comments.")

    return templates.TemplateResponse("comment_edit.html", {"request": request, "comment": comment})


@router.post("/comment/edit/{comment_id}")
async def submit_edit_comment(comment_id: int,
                              content: str = Form(...),
                              db: Session = Depends(get_db),
                              current_user: User = Depends(auth_service.get_current_user_optional)
                              ):

    comment = db.query(Comment).filter(Comment.id == comment_id, Comment.user_id == current_user.id).first()

    if not comment:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Comment not found.")

    comment.content = content
    comment.updated_at = datetime.now()
    db.commit()

    return RedirectResponse(url=f"/picture/{comment.picture_id}", status_code=status.HTTP_303_SEE_OTHER)


@router.post("/comment/delete/{comment_id}")
async def delete_comment(comment_id: int,
                         db: Session = Depends(get_db),
                         current_user: User = Depends(auth_service.get_current_user_optional)):
    if not current_user:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Musisz być zalogowany.")

    if not current_user.admin and not current_user.moderator:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Brak uprawnień do usunięcia komentarza.")

    comment = db.query(Comment).filter(Comment.id == comment_id).first()

    if not comment:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Komentarz nie został znaleziony.")

    db.delete(comment)
    db.commit()

    return RedirectResponse(url=f"/picture/{comment.picture_id}", status_code=status.HTTP_303_SEE_OTHER)


@router.post("/picture/delete/{picture_id}")
async def delete_picture(picture_id: int,
                         db: Session = Depends(get_db),
                         current_user: User = Depends(auth_service.get_current_user_optional)
                         ):

    if not current_user:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Authentication required.")

    picture = db.query(Picture).filter(Picture.id == picture_id).first()
    if not picture:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Picture not found.")

    # Check if the current user is the uploader or an admin
    if picture.user_id != current_user.id and not current_user.admin:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN,
                            detail="You do not have permission to perform this action.")

    db.delete(picture)
    db.commit()

    return RedirectResponse(url="/", status_code=status.HTTP_303_SEE_OTHER)


@router.get("/picture/edit/{picture_id}", response_class=HTMLResponse)
async def edit_picture_form(request: Request,
                            picture_id: int,
                            db: Session = Depends(get_db),
                            current_user: User = Depends(auth_service.get_current_user_optional)
                            ):

    if not current_user:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Authentication required.")

    picture = db.query(Picture).filter(Picture.id == picture_id, Picture.user_id == current_user.id).first()
    if not picture:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Picture not found or you don't have permission to edit it.")

    return templates.TemplateResponse("picture_edit.html", {"request": request, "picture": picture})


@router.post("/picture/edit/{picture_id}")
async def edit_picture(picture_id: int,
                       description: str = Form(...),
                       db: Session = Depends(get_db),
                       current_user: User = Depends(auth_service.get_current_user_optional)
                       ):

    if not current_user:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Authentication required.")

    picture = db.query(Picture).filter(Picture.id == picture_id, Picture.user_id == current_user.id).first()
    if not picture:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Picture not found or you don't have permission to edit it.")

    picture.description = description
    db.commit()

    return RedirectResponse(url=f"/picture/{picture_id}", status_code=status.HTTP_303_SEE_OTHER)


@router.get("/login", response_class=HTMLResponse)
async def authentication_page(request: Request):
    return templates.TemplateResponse('login.html', {"request": request})


@router.post("/login", response_class=HTMLResponse)
async def login_form(request: Request,
                     db: Session = Depends(get_db)):
    form = await request.form()
    email = form.get('email')
    password = form.get('password')

    user = db.query(User).filter(User.email == email).first()

    if user:
        if user.ban_status:
            msg = 'User is banned.'
            context = {'request': request, 'msg': msg}
            return templates.TemplateResponse('login.html', context)

        if auth_service.verify_password(password, user.password):
            data = {"sub": email}
            jwt_token = auth_service.create_access_token(data=data)
            jwt_refresh_token = auth_service.create_refresh_token(data=data)
            pictures = db.query(Picture).all()

            context = {'request': request, 'user': user, 'pictures': pictures}
            response = templates.TemplateResponse('home.html', context)
            response.set_cookie(key='access_token', value=f'Bearer {jwt_token}', httponly=True)
            response.set_cookie(key="refresh_token", value=jwt_refresh_token, httponly=True)
            return response

    msg = 'Incorrect Username or Password'
    context = {'request': request, 'msg': msg}
    return templates.TemplateResponse('login.html', context)


@router.get("/logout", response_class=HTMLResponse)
async def logout(request: Request, response: Response):
    response = RedirectResponse(url="/login", status_code=status.HTTP_303_SEE_OTHER)
    response.delete_cookie(key="access_token")
    response.delete_cookie(key="refresh_token")
    return response


@router.get('/register', response_class=HTMLResponse)
async def register(request: Request):\
    return templates.TemplateResponse('register.html', {"request": request})


@router.post('/register', response_class=HTMLResponse)
async def register_user(request: Request,
                        username: str = Form(...),
                        email: str = Form(...),
                        password: str = Form(...),
                        password2: str = Form(),
                        db: Session = Depends(get_db)
                        ):

    validation1 = db.query(User).filter(User.username == username).first()

    validation2 = db.query(User).filter(User.email == email).first()

    if password != password2 or validation1 is not None or validation2 is not None:
        msg = 'Invalid registration request'
        context = {'request': request, 'msg': msg}

        return templates.TemplateResponse('register.html', context)

    user_model = User()
    user_model.username = username
    user_model.email = email
    user_model.password = auth_service.get_password_hash(password)
    user_model.confirmed = True
    user_model.crated_at = datetime.now()

    db.add(user_model)
    db.commit()

    msg = 'User successfully created'
    context = {'request': request, 'msg': msg}
    return templates.TemplateResponse('login.html', context)
