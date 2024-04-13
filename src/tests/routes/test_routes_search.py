
def test_search_picture(client, picture_s):
    picture = picture_s
    print(picture.dict())
    keyword = None
    sort_by = None
    sort_order = None

    if sort_by not in ["rating", "created_at"]:
        sort_by = "created_at"

    if sort_order not in ["asc", "desc"]:
        sort_order = "desc"

    response1 = client.post(
        f"/api/search/pictures?keyword={keyword}&sort_by={sort_by}&sort_order={sort_order}",
    )

    assert response1.status_code == 404
    assert response1.json() == {"detail": "Picture not found"}
