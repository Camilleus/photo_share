from datetime import datetime

from fastapi import Request, HTTPException, APIRouter, Form, UploadFile, File
from fastapi.params import Depends
from sqlalchemy.orm import Session
from starlette import status
from starlette.responses import HTMLResponse, RedirectResponse, Response
from starlette.templating import Jinja2Templates

from src.database.db import get_db
from src.database.models import User, Picture, Comment, Rating
from src.services.auth import auth_service
import src.repository.pictures as picture_repository
import src.repository.rating as rating_repository
import src.repository.stories as story_repository
from src.conf.cloudinary import configure_cloudinary, generate_random_string
from src.services.qr import generate_qr_and_upload_to_cloudinary
import cloudinary
import cloudinary.uploader
from fastapi import HTTPException, status

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
    pictures = db.query(Picture).order_by(Picture.created_at.desc()).all()
    stories = await story_repository.get_active_stories(db)

    # Check if user has posted a BeReal in the last 24 hours
    user_has_posted_bereal = False
    if user.last_bereal_post_at:
        time_diff = datetime.now() - user.last_bereal_post_at
        if time_diff.total_seconds() < 24 * 3600:
            user_has_posted_bereal = True

    context = {
        'request': request,
        'user': user,
        'pictures': pictures,
        'stories': stories,
        'user_has_posted_bereal': user_has_posted_bereal
    }
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
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    uploaded_images_count = db.query(Picture).filter(Picture.user_id == user_id).count()
    added_comments_count = db.query(Comment).filter(Comment.user_id == user_id).count()

    # Fetch user's content
    user_pictures = db.query(Picture).filter(Picture.user_id == user_id, Picture.media_type == 'image').all()
    user_videos = db.query(Picture).filter(Picture.user_id == user_id, Picture.media_type == 'video').all()
    user_reels = db.query(Picture).filter(Picture.user_id == user_id, Picture.media_type == 'reel').all()
    user_gifs = db.query(Picture).filter(Picture.user_id == user_id, Picture.media_type == 'gif').all()
    user_stories = db.query(Story).filter(Story.user_id == user_id).all()

    context = {
        "request": request,
        "user": user,
        'current_user': current_user,
        "uploaded_images_count": uploaded_images_count,
        "added_comments_count": added_comments_count,
        "user_pictures": user_pictures,
        "user_videos": user_videos,
        "user_reels": user_reels,
        "user_gifs": user_gifs,
        "user_stories": user_stories
    }

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




@router.get("/picture/upload", response_class=HTMLResponse)
async def authentication_page(request: Request):
    return templates.TemplateResponse('picture_upload.html', {"request": request})


@router.get("/story/upload", response_class=HTMLResponse)
async def story_upload_page(request: Request):
    return templates.TemplateResponse('story_upload.html', {"request": request})


@router.post("/picture/upload", response_class=HTMLResponse)
async def upload_picture(request: Request,
                         picture: UploadFile = File(...),
                         picture_secondary: UploadFile = File(None),
                         is_bereal: bool = Form(False),
                         description: str = Form(...),
                         media_type: str = Form('image'),
                         metadata: str = Form("{}"),
                         qr_code: UploadFile = File(None),
                         current_user: User = Depends(auth_service.get_current_user_optional),
                         db: Session = Depends(get_db)
                         ):

    if not current_user:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Authentication required.")

    configure_cloudinary()

    # Upload main picture
    picture_name = generate_random_string()
    resource_type = 'video' if media_type in ['video', 'gif', 'reel'] else 'image'
    picture_uploaded = cloudinary.uploader.upload(picture.file, public_id=picture_name, folder='picture', overwrite=True, resource_type=resource_type)
    version = picture_uploaded.get('version')
    picture_url = cloudinary.CloudinaryImage(picture_uploaded['public_id'], resource_type=resource_type).build_url(version=version)

    # Upload secondary picture if provided
    picture_secondary_url = None
    if picture_secondary and picture_secondary.filename:
        sec_picture_name = generate_random_string()
        sec_uploaded = cloudinary.uploader.upload(picture_secondary.file, public_id=sec_picture_name, folder='picture', overwrite=True)
        picture_secondary_url = cloudinary.CloudinaryImage(sec_uploaded['public_id']).build_url(version=sec_uploaded.get('version'))

    qr = await generate_qr_and_upload_to_cloudinary(picture_url, picture_uploaded)

    uploaded_picture = await picture_repository.upload_picture(
        picture_url=picture_url,
        picture_json=picture_uploaded,
        user=current_user,
        description=description,
        qr=qr,
        db=db,
        picture_secondary_url=picture_secondary_url,
        is_bereal=is_bereal,
        media_type=media_type
    )

    if is_bereal:
        current_user.last_bereal_post_at = datetime.now()
        db.commit()

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

    average_rating = await rating_repository.get_average_of_rating(picture_id=picture_id, db=db)

    if average_rating.get('message'):
        average_rating = 0
    else:
        average_rating = average_rating.get('average_rating')

    if not picture:
        raise HTTPException(status_code=status.HTTP_204_NO_CONTENT)

    context = {'request': request,
               'picture': picture,
               'user': current_user,
               'comments': comments,
               'username_uploader': username_uploader,
               "average_rating": average_rating,
               }
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
                            current_user: User = Depends(auth_service.get_current_user_optional)):

    if not current_user:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Authentication required.")

    if current_user.admin:
        picture = db.query(Picture).filter(Picture.id == picture_id).first()
    else:
        picture = db.query(Picture).filter(Picture.id == picture_id, Picture.user_id == current_user.id).first()

    if not picture:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Picture not found or you don't have permission to edit it.")

    return templates.TemplateResponse("picture_edit.html", {"request": request, "picture": picture, "user": current_user})


@router.post("/picture/edit/{picture_id}", response_class=HTMLResponse)
async def submit_edit_picture(picture_id: int,
                              description: str = Form(...),
                              media_type: str = Form(None),
                              db: Session = Depends(get_db),
                              current_user: User = Depends(auth_service.get_current_user_optional)):

    if current_user.admin:
        picture = db.query(Picture).filter(Picture.id == picture_id).first()
    else:
        picture = db.query(Picture).filter(Picture.id == picture_id, Picture.user_id == current_user.id).first()

    if not picture:
        raise HTTPException(status_code=404, detail="Picture not found or you don't have permission to edit it.")

    picture.description = description
    if media_type:
        picture.media_type = media_type
    db.commit()

    return RedirectResponse(url=f"/picture/{picture_id}", status_code=status.HTTP_303_SEE_OTHER)


@router.post("/story/upload", response_class=HTMLResponse)
async def upload_story(request: Request,
                       story_image: UploadFile = File(...),
                       media_type: str = Form('image'),
                       description: str = Form(None),
                       current_user: User = Depends(auth_service.get_current_user_optional),
                       db: Session = Depends(get_db)
                       ):

    if not current_user:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Authentication required.")

    configure_cloudinary()
    public_id = generate_random_string()
    resource_type = 'video' if media_type in ['video', 'gif', 'reel'] else 'image'

    uploaded = cloudinary.uploader.upload(
        story_image.file,
        public_id=public_id,
        folder='stories',
        overwrite=True,
        resource_type=resource_type
    )

    image_url = cloudinary.CloudinaryImage(
        uploaded['public_id'],
        resource_type=resource_type
    ).build_url(version=uploaded.get('version'))

    await story_repository.create_story(
        image_url=image_url,
        user=current_user,
        db=db,
        media_type=media_type,
        description=description
    )

    return RedirectResponse(url="/", status_code=status.HTTP_303_SEE_OTHER)


@router.get("/story/edit/{story_id}", response_class=HTMLResponse)
async def edit_story_form(request: Request,
                          story_id: int,
                          db: Session = Depends(get_db),
                          current_user: User = Depends(auth_service.get_current_user_optional)):

    if not current_user:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Authentication required.")

    story = await story_repository.get_one_story(story_id, db)
    if not story or (story.user_id != current_user.id and not current_user.admin):
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Story not found or unauthorized")

    return templates.TemplateResponse("story_edit.html", {"request": request, "story": story, "user": current_user})


@router.post("/story/edit/{story_id}", response_class=HTMLResponse)
async def submit_edit_story(story_id: int,
                            description: str = Form(None),
                            media_type: str = Form('image'),
                            db: Session = Depends(get_db),
                            current_user: User = Depends(auth_service.get_current_user_optional)):

    story = await story_repository.get_one_story(story_id, db)
    if not story or (story.user_id != current_user.id and not current_user.admin):
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Story not found or unauthorized")

    await story_repository.update_story(story_id, media_type, description, db)

    return RedirectResponse(url="/", status_code=status.HTTP_303_SEE_OTHER)


@router.post("/story/delete/{story_id}")
async def delete_story(story_id: int,
                       db: Session = Depends(get_db),
                       current_user: User = Depends(auth_service.get_current_user_optional)):

    story = await story_repository.get_one_story(story_id, db)
    if not story or (story.user_id != current_user.id and not current_user.admin):
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Story not found or unauthorized")

    await story_repository.delete_story(story_id, db)

    return RedirectResponse(url="/", status_code=status.HTTP_303_SEE_OTHER)


@router.post("/picture/rate/{picture_id}")
async def rate_picture(picture_id: int,
                       rating: int = Form(...),
                       db: Session = Depends(get_db),
                       current_user: User = Depends(auth_service.get_current_user_optional)
                       ):
    if not current_user:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Authentication required.")

    result = await rating_repository.add_rating_to_picture(picture_id, rating, current_user, db)

    return RedirectResponse(url=f"/picture/{picture_id}", status_code=status.HTTP_303_SEE_OTHER)


@router.get("/picture/{picture_id}/ratings", response_class=HTMLResponse)
async def view_picture_ratings(request: Request,
                               picture_id: int,
                               db: Session = Depends(get_db),
                               current_user: User = Depends(auth_service.get_current_user_optional)
                               ):

    if not (current_user.admin or current_user.moderator):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Insufficient permissions.")

    ratings = (db.query(Rating, User.username)
               .join(User, Rating.user_id == User.id)
               .filter(Rating.picture_id == picture_id)
               .all())

    return templates.TemplateResponse("ratings.html", {"request": request, "ratings": ratings,
                                                       "picture_id": picture_id, "user": current_user})


@router.post("/rating/{rating_id}/delete")
async def delete_rating(rating_id: int,
                        db: Session = Depends(get_db),
                        current_user: User = Depends(auth_service.get_current_user_optional)):
    if not current_user:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Authentication required.")

    rating = db.query(Rating).filter(Rating.id == rating_id).first()

    if not rating:
        raise HTTPException(status_code=404, detail="Rating not found.")

    if not (current_user.admin or current_user.moderator or current_user.id == rating.user_id):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN,
                            detail="You do not have permission to delete this rating.")

    picture_id = rating.picture_id
    db.delete(rating)
    db.commit()

    return RedirectResponse(url=f"/picture/{picture_id}", status_code=status.HTTP_303_SEE_OTHER)


@router.get("/login", response_class=HTMLResponse)
async def authentication_page(request: Request):
    return templates.TemplateResponse('login.html', {"request": request})


@router.post("/login", response_class=HTMLResponse)
async def login_form(request: Request,
                     db: Session = Depends(get_db)
                     ):

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
async def logout(request: Request,
                 response: Response
                 ):

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
