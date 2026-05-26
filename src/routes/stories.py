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
        media_type: str = 'image',
        description: str = None,
        current_user: User = Depends(auth_service.get_current_user),
        db: Session = Depends(get_db)
):
    """
    Upload a story image or video.
    """
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

    return await repository_stories.create_story(
        image_url=image_url,
        user=current_user,
        db=db,
        media_type=media_type,
        description=description
    )

@router.put("/{story_id}", response_model=StoryResponse)
async def update_story(
        story_id: int,
        media_type: str,
        description: str,
        current_user: User = Depends(auth_service.get_current_user),
        db: Session = Depends(get_db)
):
    """
    Update a story.
    """
    story = await repository_stories.get_one_story(story_id, db)
    if not story:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Story not found")

    if story.user_id != current_user.id and not current_user.admin:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not authorized")

    return await repository_stories.update_story(story_id, media_type, description, db)

@router.delete("/{story_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_story(
        story_id: int,
        current_user: User = Depends(auth_service.get_current_user),
        db: Session = Depends(get_db)
):
    """
    Delete a story.
    """
    story = await repository_stories.get_one_story(story_id, db)
    if not story:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Story not found")

    if story.user_id != current_user.id and not current_user.admin:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not authorized")

    await repository_stories.delete_story(story_id, db)
    return None

@router.get("/", response_model=List[StoryResponse])
async def get_stories(db: Session = Depends(get_db)):
    """
    Retrieve all active stories.
    """
    return await repository_stories.get_active_stories(db)
