from datetime import datetime, timedelta
from sqlalchemy.orm import Session
from src.database.models import Story, User

async def create_story(image_url: str, user: User, db: Session, media_type: str = 'image', description: str = None) -> Story:
    """
    Creates a new story for the user.
    """
    story = Story(image_url=image_url, user_id=user.id, media_type=media_type, description=description)
    db.add(story)
    db.commit()
    db.refresh(story)
    return story

async def get_one_story(story_id: int, db: Session) -> Story:
    """
    Retrieves a story with the specified ID from the database.
    """
    return db.query(Story).filter(Story.id == story_id).first()

async def update_story(story_id: int, media_type: str, description: str, db: Session) -> Story | None:
    """
    Updates a story's media type and description.
    """
    story = db.query(Story).filter(Story.id == story_id).first()
    if story:
        story.media_type = media_type
        story.description = description
        db.commit()
        db.refresh(story)
    return story

async def delete_story(story_id: int, db: Session) -> Story | None:
    """
    Deletes a story.
    """
    story = db.query(Story).filter(Story.id == story_id).first()
    if story:
        db.delete(story)
        db.commit()
    return story

async def get_active_stories(db: Session):
    """
    Retrieves all stories posted in the last 24 hours.
    """
    day_ago = datetime.now() - timedelta(hours=24)
    return db.query(Story).filter(Story.created_at >= day_ago).all()
