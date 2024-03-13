from fastapi import APIRouter, Depends, status, Security, BackgroundTasks, Request, HTTPException, Form
from fastapi.security import OAuth2PasswordRequestForm, HTTPAuthorizationCredentials, HTTPBearer
from fastapi.responses import JSONResponse, HTMLResponse
from fastapi.templating import Jinja2Templates

from sqlalchemy.orm import Session

from src.database.models import User
from src.services.email import send_verification_email, send_reset_email
from src.database.db import get_db
from src.schemas import UserModel, UserResponse, TokenModel, RequestEmail, ResetPasswordModel, ChangePasswordModel
from src.repository import users as repository_users
from src.services.auth import auth_service

router = APIRouter(prefix='/auth', tags=["auth"])
security = HTTPBearer()
templates = Jinja2Templates(directory="templates")


@router.post("/signup", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
async def signup(body: UserModel,
                 background_tasks: BackgroundTasks,
                 request: Request, db: Session = Depends(get_db)) -> JSONResponse | dict:
    """
    Sign up a new user.

    Args:
        body (UserModel): Data for the new user.
        background_tasks (BackgroundTasks): Background tasks to execute.
        request (Request): The incoming request.
        db (Session): SQLAlchemy database session.

    Returns:
        dict: Response containing the new user and a confirmation message.
    """
    exist_user = await repository_users.get_user_by_email(body.email, db)

    if exist_user:
        return JSONResponse(status_code=409, content={"detail": "Account already exists."})

    body.password = auth_service.get_password_hash(body.password)
    new_user = await repository_users.create_user(body, db)
    background_tasks.add_task(send_verification_email, new_user.email, str(request.base_url))

    return {"user": new_user, "detail": "User successfully created. Check your email for confirmation."}


@router.post("/login", response_model=TokenModel)
async def login(body: OAuth2PasswordRequestForm = Depends(),
                db: Session = Depends(get_db)) -> JSONResponse | dict:
    """
    Log in a user and generate access and refresh tokens.

    Args:
        body (OAuth2PasswordRequestForm): Form containing user credentials.
        db (Session): SQLAlchemy database session.

    Returns:
        dict: Response containing access and refresh tokens.
    """
    user = await repository_users.get_user_by_email(body.username, db)

    if user is None:
        return JSONResponse(status_code=401, content={"detail": "Invalid email."})

    if not user.confirmed:
        return JSONResponse(status_code=401, content={"detail": "Email not confirmed."})

    if not auth_service.verify_password(body.password, user.password):
        return JSONResponse(status_code=401, content={"detail": "Invalid password."})

    if user.ban_status:
        return JSONResponse(status_code=403, content={"detail": "Your account has been banned."})

    access_token = auth_service.create_access_token(data={"sub": user.email})
    refresh_token_ = auth_service.create_refresh_token(data={"sub": user.email})

    await repository_users.update_token(user, refresh_token_, db)
    return {"access_token": access_token, "refresh_token": refresh_token_, "token_type": "bearer"}



@router.get('/refresh_token', response_model=TokenModel)
async def refresh_token(credentials: HTTPAuthorizationCredentials = Security(security),
                        db: Session = Depends(get_db)) -> JSONResponse | dict:
    """
    Refresh the access token using a valid refresh token.

    Args:
        credentials (HTTPAuthorizationCredentials): Credentials containing the refresh token.
        db (Session): SQLAlchemy database session.

    Returns:
        dict: Response containing a new access token and refresh token.
    """
    token = credentials.credentials
    email = await auth_service.decode_refresh_token(token)
    user = await repository_users.get_user_by_email(email, db)

    if user.refresh_token != token:
        await repository_users.update_token(user, None, db)
        return JSONResponse(status_code=401, content={"detail": "Invalid refresh token."})

    access_token = auth_service.create_access_token(data={"sub": email})
    refresh_token_ = auth_service.create_refresh_token(data={"sub": email})

    await repository_users.update_token(user, refresh_token_, db)
    return {"access_token": access_token, "refresh_token": refresh_token_, "token_type": "bearer"}


@router.get('/confirmed_email/{token}', response_model=None)
async def confirmed_email(token: str,
                          db: Session = Depends(get_db)) -> JSONResponse | dict:
    """
    Confirm the email address for a user using a confirmation token.

    Args:
        token (str): Confirmation token.
        db (Session): SQLAlchemy database session.

    Returns:
        dict: Response message.
    """
    email = await auth_service.get_email_from_token(token)
    user = await repository_users.get_user_by_email(email, db)

    if user is None:
        return JSONResponse(status_code=400, content={"detail": "Verification error."})
    if user.confirmed:
        return {"message": "Your email is already confirmed."}

    await repository_users.confirmed_email(email, db)
    return {"message": "Email confirmed."}


@router.post('/request_email')
async def request_email(body: RequestEmail,
                        background_tasks: BackgroundTasks,
                        request: Request,
                        db: Session = Depends(get_db)) -> dict:
    """
    Request email confirmation for a user.

    Args:
        body (RequestEmail): Request body containing user email.
        background_tasks (BackgroundTasks): Background tasks to execute.
        request (Request): The incoming request.
        db (Session): SQLAlchemy database session.

    Returns:
        dict: Response message.
    """
    user = await repository_users.get_user_by_email(body.email, db)

    if user.confirmed:
        return {"message": "Your email is already confirmed."}
    if user.confirmed is False:
        background_tasks.add_task(send_verification_email, user.email, str(request.base_url))
        return {"message": "Check your email for confirmation."}


@router.post('/reset_password/request')
async def request_password_reset(body: RequestEmail,
                                 background_tasks: BackgroundTasks,
                                 request: Request,
                                 db: Session = Depends(get_db)) -> JSONResponse:
    """
    Request email reset password for a user.

    Args:
        body (RequestEmail): Request body containing user email.
        background_tasks (BackgroundTasks): Background tasks to execute.
        request (Request): The incoming request.
        db (Session): SQLAlchemy database session.

    Returns:
        dict: Response message.
    """
    user = await repository_users.get_user_by_email(body.email, db)

    if user is None:
        return JSONResponse(status_code=400, content={"detail": "Verification error."})
    else:
        background_tasks.add_task(send_reset_email, user.email, str(request.base_url))
        return JSONResponse(status_code=200, content={"message": "Password reset email sent."})


@router.get("/reset_password/{token}", response_class=HTMLResponse)
async def reset_password(request: Request, token: str, error: str = None):
    """
    Display the password reset form.

    Args:
        request (Request): The incoming request.
        token (str): Reset password token.
        error (str): Error message.

    Returns:
        HTMLResponse: HTML template response.
    """
    return templates.TemplateResponse(
        request=request,
        name="reset_password.html",
        context={"request": request, "token": token, "error": error})


@router.post('/reset_password/{token}', response_model=None)
async def reset_password_post(token: str,
                              password_data: ResetPasswordModel,
                              db: Session = Depends(get_db)) -> JSONResponse | dict:
    """
    Handle the submission of the password reset form.
    """
    email = await auth_service.get_email_from_token(token)
    user = await repository_users.get_user_by_email(email, db)

    new_password = password_data.new_password

    if user is None:
        return JSONResponse(status_code=400, content={"detail": "Verification error."})

    await repository_users.upgrade_password(user, new_password, db)
    return JSONResponse(status_code=200, content={"message": "Password reset successfully."})


@router.post('/change_password')
async def change_password(change_password_data: ChangePasswordModel,
                          db: Session = Depends(get_db),
                          current_user: User = Depends(auth_service.get_current_user)
                          ) -> JSONResponse:
    """
    Change the password for the current user.

    """
    current_password = change_password_data.current_password
    new_password = change_password_data.new_password
    confirm_password = change_password_data.confirm_password

    if not auth_service.verify_password(current_password, current_user.password):
        return JSONResponse(status_code=401,
                            content={"detail": "Current password is incorrect."})
    elif new_password != confirm_password:
        return JSONResponse(status_code=400,
                            content={"message": "The provided passwords do not match."})

    await auth_service.upgrade_password(current_user, new_password, db)
    return JSONResponse(status_code=200,
                        content={"message": "Password changed successfully."})

