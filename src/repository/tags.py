from typing import List
from sqlalchemy.orm import Session
from src.database.models import Tag, PictureTagsAssociation
from src.schemas import TagModel, TagsResponseModel

async def add_tags_to_db(picture_id: int, tags: List[str], db: Session) -> TagsResponseModel:
    """
    Add new tags to the database.

    This function adds new tags to the database. If a tag with the same name already
    exists in the database, it is skipped.

    Parameters:
    - picture_id (int): The ID of the picture to which the tags will be associated.
    - tags (Union[List[str], str]): A list of tag names to be added to the database. If a single tag
      is provided as a string, it will be converted to a list internally.
    - db (Session): The SQLAlchemy session used to interact with the database.

    Returns:
    - TagsResponseModel: A response model containing two lists of TagModel instances,
      representing newly created tags and existing tags in the database.
    
    Raises:
    - TypeError: If the provided tags are not in the correct format (list of strings).
    - ValueError: If the number of tags exceeds the maximum limit.
    """
    max_limit = 5
    if len(tags) > max_limit:
        raise ValueError(f"Number of tags exceeds the maximum limit of {max_limit}")
    elif not isinstance(tags, list):
        raise TypeError("Tags must be provided as a list.")
    elif not all(isinstance(tag, str) for tag in tags):
        raise TypeError("Tags must be strings.")

    if not isinstance(picture_id, int):
        raise TypeError("Picture_ID must be provided as an integer.")


    existing_tags = db.query(Tag).filter(Tag.name.in_(tags)).all()
    tag_name_to_id = {tag.name: tag.id for tag in existing_tags}

    new_tags = [Tag(name=tag_name) for tag_name in tags if tag_name not in tag_name_to_id]
    db.add_all(new_tags)
    db.commit()

    for tag in new_tags:
        db.refresh(tag)

    all_tags = existing_tags + new_tags

    existing_associations = db.query(PictureTagsAssociation).filter(
        PictureTagsAssociation.picture_id == picture_id
    ).all()

    for association in existing_associations:
        db.delete(association)
    db.commit()

    associations_to_add = [
        PictureTagsAssociation(picture_id=picture_id, tag_id=tag.id)
        for tag in all_tags
    ]
    db.add_all(associations_to_add)
    db.commit()

    return TagsResponseModel(new_tags=[TagModel(id=tag.id, name=tag.name) for tag in new_tags],
                             existing_tags=[TagModel(id=tag.id, name=tag.name) for tag in existing_tags])
