from redis_utils import redis_client


def test_create_blog(client):
    response = client.post(
        "/api/blog", json={"title": "My Test Blog", "content": "Some content"}
    )
    assert response.status_code == 200
    data = response.json()
    assert data["title"] == "My Test Blog"
    assert data["content"] == "Some content"
    assert "id" in data


def test_get_all_blogs(client):
    # Create a blog first
    client.post("/api/blog", json={"title": "All Blogs Test", "content": "Content"})

    # Check cache is empty
    assert redis_client.get("blogs_all") is None

    response = client.get("/api/blog/all")
    assert response.status_code == 200
    blogs = response.json()
    assert isinstance(blogs, list)
    assert any(b["title"] == "All Blogs Test" for b in blogs)

    # Check cache populated
    cached = redis_client.get("blogs_all")
    assert cached is not None


def test_get_user_blogs(client, test_user):
    # Create two blogs for this user
    client.post("/api/blog", json={"title": "User Blog 1", "content": "abc"})
    client.post("/api/blog", json={"title": "User Blog 2", "content": "xyz"})

    # Check cache is empty
    user_cache_key = f"blogs_user_{test_user.id}"
    assert redis_client.get(user_cache_key) is None

    response = client.get("/api/blog")
    assert response.status_code == 200
    blogs = response.json()
    assert isinstance(blogs, list)
    assert len(blogs) >= 2

    # Check cache populated
    cached = redis_client.get(user_cache_key)
    assert cached is not None


def test_get_single_blog(client):
    # Create blog
    response = client.post(
        "/api/blog", json={"title": "Single Blog Test", "content": "Hello"}
    )
    blog_id = response.json()["id"]

    # Cache should be empty
    cache_key = f"blog_{blog_id}_user_{response.json()['owner_id']}"
    assert redis_client.get(cache_key) is None

    # Fetch the blog
    response = client.get(f"/api/blog/{blog_id}")
    assert response.status_code == 200
    data = response.json()
    assert data["title"] == "Single Blog Test"
    assert data["content"] == "Hello"

    # Now cache should be filled
    cached = redis_client.get(cache_key)
    assert cached is not None


def test_get_nonexistent_blog(client):
    response = client.get("/api/blog/999999")
    assert response.status_code == 404
    assert response.json()["detail"] == "Blog not found"


def test_update_blog(client):
    # Create blog
    response = client.post(
        "/api/blog", json={"title": "Old Title", "content": "Old content"}
    )
    blog_id = response.json()["id"]

    # Update blog
    response = client.put(f"/api/blog/{blog_id}", json={"title": "Updated Title"})
    assert response.status_code == 200
    data = response.json()
    assert data["title"] == "Updated Title"
    assert data["content"] == "Old content"


def test_update_nonexistent_blog(client):
    response = client.put("/api/blog/999999", json={"title": "Test"})
    assert response.status_code == 404
    assert response.json()["detail"] == "Blog not found"


def test_delete_blog(client):
    # Create blog
    response = client.post("/api/blog", json={"title": "Delete Me", "content": "Bye"})
    blog_id = response.json()["id"]

    # Delete blog
    response = client.delete(f"/api/blog/{blog_id}")
    assert response.status_code == 204

    # Verify it no longer exists
    response = client.get(f"/api/blog/{blog_id}")
    assert response.status_code == 404


def test_delete_nonexistent_blog(client):
    response = client.delete("/api/blog/999999")
    assert response.status_code == 404
    assert response.json()["detail"] == "Blog not found"
