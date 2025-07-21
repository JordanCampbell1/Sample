from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from auth import get_current_user
from schemas import BlogCreate, BlogOut, BlogUpdate
from models import Blog, User
from typing import List
from database import get_db
from redis_utils import publish_event, redis_client
import json

router = APIRouter(prefix="/blog")


# Create Blog
@router.post("", response_model=BlogOut)
async def create_blog(
    blog: BlogCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    new_blog = Blog(title=blog.title, content=blog.content, owner_id=current_user.id)
    db.add(new_blog)
    db.commit()
    db.refresh(new_blog)

    # Clear cache for this blog
    cache_key = f"blog_{new_blog.id}_user_{current_user.id}"
    redis_client.delete(cache_key)
    # Clear cache for all blogs of the user
    user_cache_key = f"blogs_user_{current_user.id}"
    redis_client.delete(user_cache_key)
    # Clear cache for all blogs
    redis_client.delete("blogs_all")

    await publish_event("create_blog", f"New blog: {new_blog.title}")

    return new_blog


# Get All Blogs
@router.get("/all", response_model=List[BlogOut])
async def get_all_blogs(
    db: Session = Depends(get_db), current_user: User = Depends(get_current_user)
):
    cache_key = "blogs_all"

    cached_data = redis_client.get(cache_key)
    if cached_data:
        print("⛳️ Fetched blog list from Redis cache")
        # Return a list of validated BlogOut models
        return json.loads(cached_data)

    print("⚠️ Cache miss — fetching blog list from DB")
    blogs = db.query(Blog).all()

    # Convert to list of dicts via model_validate
    blogs_data = [BlogOut.model_validate(blog).model_dump() for blog in blogs]

    # Cache the list as JSON string, 5-minute expiry
    redis_client.set(cache_key, json.dumps(blogs_data), ex=300)

    return [BlogOut.model_validate(blog) for blog in blogs_data]


# Get All Blogs (for current user)
@router.get("", response_model=List[BlogOut])
async def get_blogs(
    db: Session = Depends(get_db), current_user: User = Depends(get_current_user)
):

    cache_key = f"blogs_user_{current_user.id}"
    # Check if data is cached
    cached_data = redis_client.get(cache_key)

    if cached_data:
        print("⛳️ Fetched from Redis cache")

        return json.loads(cached_data)

    print("⚠️ Cache miss — fetching from DB")

    blogs = db.query(Blog).filter(Blog.owner_id == current_user.id).all()

    blogs_list = [
        {"id": b.id, "title": b.title, "content": b.content, "owner_id": b.owner_id}
        for b in blogs
    ]

    # Cache result in Redis
    redis_client.setex(cache_key, 60 * 60, json.dumps(blogs_list))  # cache for 1 hour

    return blogs


# Get Single Blog by ID (for current user)
@router.get("/{blog_id}", response_model=BlogOut)
async def get_blog(
    blog_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):

    # Create a unique cache key for the blog and user
    cache_key = f"blog_{blog_id}_user_{current_user.id}"

    # Check if data is cached
    cached_data = redis_client.get(cache_key)

    if cached_data:
        print("⛳️ Fetched from Redis cache")
        return json.loads(cached_data)

    print("⚠️ Cache miss — fetching from DB")

    blog = (
        db.query(Blog)
        .filter(Blog.id == blog_id, Blog.owner_id == current_user.id)
        .first()
    )

    if not blog:
        raise HTTPException(status_code=404, detail="Blog not found")

    # Convert ORM object to BlogOut Pydantic model
    blog_data = BlogOut.model_validate(blog)

    # Cache it
    redis_client.set(cache_key, blog_data.model_dump_json(), ex=300)

    return blog


# Update Blog (for current user)
@router.put("/{blog_id}", response_model=BlogOut)
async def update_blog(
    blog_id: int,
    updated_data: BlogUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):

    blog = (
        db.query(Blog)
        .filter(Blog.id == blog_id, Blog.owner_id == current_user.id)
        .first()
    )
    if not blog:
        raise HTTPException(status_code=404, detail="Blog not found")

    # Only update fields that were provided
    if updated_data.title is not None:
        blog.title = updated_data.title
    if updated_data.content is not None:
        blog.content = updated_data.content

    # Clear cache for this blog
    cache_key = f"blog_{blog_id}_user_{current_user.id}"
    redis_client.delete(cache_key)
    # Clear cache for all blogs of the user
    user_cache_key = f"blogs_user_{current_user.id}"
    redis_client.delete(user_cache_key)
    # Clear cache for all blogs
    redis_client.delete("blogs_all")

    await publish_event("update_blog", f"Updated blog: {blog.title}")

    db.commit()
    db.refresh(blog)
    return blog


# Delete Blog (for current user)
@router.delete("/{blog_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_blog(
    blog_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    blog = (
        db.query(Blog)
        .filter(Blog.id == blog_id, Blog.owner_id == current_user.id)
        .first()
    )
    if not blog:
        raise HTTPException(status_code=404, detail="Blog not found")

    # Clear cache for this blog
    cache_key = f"blog_{blog_id}_user_{current_user.id}"
    redis_client.delete(cache_key)
    # Clear cache for all blogs of the user
    user_cache_key = f"blogs_user_{current_user.id}"
    redis_client.delete(user_cache_key)
    # Clear cache for all blogs
    redis_client.delete("blogs_all")

    db.delete(blog)
    db.commit()
    return {"detail": "Blog deleted successfully"}
