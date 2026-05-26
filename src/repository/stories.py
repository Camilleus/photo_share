from datetime import datetime, timedelta
from sqlalchemy.orm import Session
from src.database.models import Story, User

async def create_story(image_url: str, user: User, db: Session) -> Story:
    """
    Creates a new story for the user.
    """
    story = Story(image_url=image_url, user_id=user.id)
    db.add(story)
    db.commit()
    db.refresh(story)
    return story

async def get_active_stories(db: Session):
    """
    Retrieves all stories posted in the last 24 hours.
    """
    day_ago = datetime.now() - timedelta(hours=24)
    return db.query(Story).filter(Story.created_at >= day_ago).all()
