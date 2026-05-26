from typing import List
from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, status
from sqlalchemy.orm import Session
import cloudinary
import cloudinary.uploader

from src.database.db import get_db
from src.database.models import User, Story
from src.schemas import StoryResponse
from src.repository import stories as repository_stories
from src.services.auth import auth_service
from src.conf.cloudinary import configure_cloudinary, generate_random_string

router = APIRouter(prefix='/stories', tags=["stories"])

@router.post("/upload", status_code=status.HTTP_201_CREATED, response_model=StoryResponse)
async def upload_story(
        story_image: UploadFile = File(),
        current_user: User = Depends(auth_service.get_current_user),
        db: Session = Depends(get_db)
):
    """
    Upload a story image.
    """
    configure_cloudinary()
    public_id = generate_random_string()
    uploaded = cloudinary.uploader.upload(story_image.file, public_id=public_id, folder='stories', overwrite=True)
    image_url = cloudinary.CloudinaryImage(uploaded['public_id']).build_url(version=uploaded.get('version'))

    return await repository_stories.create_story(image_url=image_url, user=current_user, db=db)

@router.get("/", response_model=List[StoryResponse])
async def get_stories(db: Session = Depends(get_db)):
    """
    Retrieve all active stories.
    """
    return await repository_stories.get_active_stories(db)
