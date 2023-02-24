import pytest
from typing import List
from app import schemas


def test_get_all_posts(authorized_client, test_posts):
    res = authorized_client.get("/posts/")
    posts_map = map(lambda post: schemas.PostOut(**post), res.json())

    posts = list(posts_map)
    assert len(posts) == len(test_posts)
    assert res.status_code == 200

def test_unauthorize_user_get_all_posts(client, test_posts):
    res = client.get("/posts/")
    assert res.status_code == 401

def test_unauthorize_user_get_one_post(client, test_posts):
    res = client.get(f"/posts/{test_posts[0].id}")
    assert res.status_code == 401

def test_get_one_post_not_exist(authorized_client, test_posts):
    res = authorized_client.get("/posts/1000")
    assert res.status_code == 404

def test_get_one_post(authorized_client, test_posts):
    res = authorized_client.get(f"/posts/{test_posts[0].id}")
    post = schemas.PostOut(**res.json())
    assert res.status_code == 200
    assert post.Post.id == test_posts[0].id

@pytest.mark.parametrize("title, content, published, status_code", [
    ("Test title", "Some interesting content", True, 201),
    ("Test title2", "Some more interesting content", False, 201)
])
def test_create_post(title: str, content: str, published: bool, 
                    status_code: int, authorized_client, test_user):
    res = authorized_client.post("/posts/", json={"title": title, "content": content, 
                                                  "published": published})
    
    created_post = schemas.PostResponseDto(**res.json())
    assert res.status_code == status_code
    assert created_post.title == title
    assert created_post.content == content
    assert created_post.published == published
    assert created_post.owner_id == test_user['id']

def test_create_post_default_published_true(authorized_client):
    res = authorized_client.post("/posts/", json={"title": "Some title", "content": "Some interesting content"})
    created_post = schemas.PostResponseDto(**res.json())
    assert created_post.published == True

def test_unauthorized_user_create_post(client):
    res = client.post("/posts/", json={"title": "Some title", "content": "Some interesting content"})
    assert res.status_code == 401


def test_unauthorized_user_delete_post(client, test_posts):
    res = client.delete(f"/posts/{test_posts[0].id}")
    assert res.status_code == 401

def test_delete_post_sucess(authorized_client, test_posts):
    res = authorized_client.delete(f"/posts/{test_posts[0].id}")
    assert res.status_code == 204

def test_delete_none_existent_post(authorized_client):
    res = authorized_client.delete("/posts/1000")
    assert res.status_code == 404

def test_delete_other_user_post(authorized_client, test_posts):
    res = authorized_client.delete(f"/posts/{test_posts[3].id}")
    assert res.status_code == 403

def test_update_post(authorized_client, test_user, test_posts):
    data = {
        "title": "updated title",
        "content": "updated content",
        "published": True
    }

    res = authorized_client.put(f"/posts/{test_posts[0].id}", json=data)
    updated_post = schemas.PostResponseDto(**res.json())

    assert res.status_code == 200
    assert updated_post.title == data['title']
    assert updated_post.content == data['content']

def test_update_other_user_post(authorized_client, test_user, test_user2, test_posts):
    data = {
        "title": "updated title",
        "content": "updated content",
        "published": True
    }
    res = authorized_client.put(f"/posts/{test_posts[3].id}", json=data)
    assert res.status_code == 403

def test_unauthorized_user_update_post(client, test_posts):
    data = {
        "title": "updated title",
        "content": "updated content",
        "published": True
    }
    res = client.put(f"/posts/{test_posts[0].id}", json=data)
    assert res.status_code == 401

def test_update_none_existent_post(authorized_client):
    data = {
        "title": "updated title",
        "content": "updated content",
        "published": True
    }
    res = authorized_client.put("/posts/1000", json=data)
    assert res.status_code == 404