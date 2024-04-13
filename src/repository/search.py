from sqlalchemy.orm import Session
from fastapi import HTTPException, Depends
from typing import List, Optional
from sqlalchemy import or_

from src.database.models import Picture, Tag, PictureTagsAssociation
from src.database.db import get_db
from src.schemas import PictureResponse


async def search_pictures(keyword: Optional[str] = None,
                          sort_by: Optional[str] = "created_at",
                          sort_order: Optional[str] = "desc",
                          db: Session = Depends(get_db)
                          ) -> List[PictureResponse]:
    """
    Searches for pictures based on keywords, sort criteria, and order. It allows for filtering pictures
    by tags or description that match the keyword, and then sorts the results according to the specified
    sort criteria and order.

    Parameters:
    - `keyword` (Optional[str]): The keyword to search for within picture tags and descriptions.
                                 If None, the function will return all pictures.
    - `sort_by` (Optional[str]): The field by which the results should be sorted. Defaults to "created_at".
                                 Allowed values are "rating" and "created_at".
    - `sort_order` (Optional[str]): The order in which the results should be sorted. Defaults to "desc" (descending).
                                    Allowed values are "asc" (ascending) and "desc" (descending).
    - `db` (Session): The database session.

    Returns:
    - List[PictureResponse]: A list of `PictureResponse` objects, each representing a picture that matches the search criteria.
                             Each `PictureResponse` includes picture ID, description, picture URL, average rating, creation date,
                             user ID, associated tags IDs, and a QR code picture URL.

    Raises:
    - HTTPException: If no pictures are found that match the search criteria, a 404 error is raised with the detail "Picture not found".

    The function first filters tags by the keyword and then finds pictures associated with these tags. It also searches
    within picture descriptions for the keyword. The resulting list of pictures is then sorted based on the specified
    `sort_by` and `sort_order` parameters. If no keyword is provided, all pictures are considered in the search. The
    function ensures that the sorting parameters are valid and defaults them if necessary.
    """

    if sort_by not in ["rating", "created_at"]:
        sort_by = "created_at"

    if sort_order not in ["asc", "desc"]:
        sort_order = "desc"

    tags_ids = [tag.id for tag in db.query(Tag).filter(Tag.name.like(f"%{keyword}%")).all()]

    pictures_ids = [pic_id for (pic_id,) in db.query(PictureTagsAssociation.picture_id).filter(
        PictureTagsAssociation.tag_id.in_(tags_ids)).all()]

    pictures = db.query(Picture).filter(
        or_(
            Picture.description.like(f"%{keyword}%"),
            Picture.id.in_(pictures_ids)
        )
    ).all()

    if not pictures:
        raise HTTPException(status_code=404, detail="Picture not found")

    pictures = sorted(pictures, key=lambda x: getattr(x, sort_by), reverse=(sort_order == "desc"))

    picture_responses = []
    for picture in pictures:
        tag_ids = [tag.id for tag in picture.tags]
        picture_response = PictureResponse(
            id=picture.id,
            description=picture.description,
            picture_url=picture.picture_url,
            average_rating=picture.average_rating,
            created_at=picture.created_at,
            user_id=picture.user_id,
            tags=tag_ids,
            qr_code_picture=picture.qr_code_picture
        )
        picture_responses.append(picture_response)

    return picture_responses
