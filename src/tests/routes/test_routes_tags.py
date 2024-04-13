import pytest
from fastapi import HTTPException
from sqlalchemy.orm import Session
from src.routes.tags import add_tags
from src.repository import tags as repository_tags
from unittest.mock import MagicMock, patch

@pytest.mark.asyncio
async def test_add_tag_success(session):
    tags = ["kotek", "piesek", "myszka", "szczurek", "pythnonik"]
    picture_id = 1
    
    async def mock_add_tags_to_db(picture_id: int, tags: list, db: Session):
        return {"new_tags": tags, "existing_tags": []}

    with patch.object(repository_tags, "add_tags_to_db", new=mock_add_tags_to_db):
        response = await add_tags(picture_id=picture_id, tags=tags, db=session)
        assert response["new_tags"] == tags
        assert response["existing_tags"] == []

@pytest.mark.asyncio
async def test_add_tag_fail(session):
    tags = ["kotek", "piesek", "myszka", "szczurek", "pythnonik", "rybka"]
    picture_id = 1
    
    async def mock_add_tags_to_db(picture_id: int, tags: list, db: Session):
        raise HTTPException(status_code=400, detail="Tags could not be created.")

    with patch.object(repository_tags, "add_tags_to_db", new=mock_add_tags_to_db):
        with pytest.raises(HTTPException):
            await add_tags(picture_id=picture_id, tags=tags, db=session)