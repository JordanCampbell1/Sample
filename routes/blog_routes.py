from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from auth import get_current_user
from schemas import BlogCreate, BlogOut, BlogUpdate
from models import Blog, User
from typing import List
from database import get_db

router = APIRouter(prefix="/blog")

# Create Blog
@router.post("", response_model=BlogOut)
def create_blog(blog: BlogCreate, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    new_blog = Blog(title=blog.title, content=blog.content, owner_id=current_user.id)
    db.add(new_blog)
    db.commit()
    db.refresh(new_blog)
    return new_blog

# Get All Blogs that exists
@router.get("/all", response_model=List[BlogOut])
def get_blogs(db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    return db.query(Blog).all()

# Get All Blogs (for current user)
@router.get("", response_model=List[BlogOut])
def get_blogs(db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    return db.query(Blog).filter(Blog.owner_id == current_user.id).all()

# Get Single Blog by ID (for current user)
@router.get("/{blog_id}", response_model=BlogOut)
def get_blog(blog_id: int, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    blog = db.query(Blog).filter(Blog.id == blog_id, Blog.owner_id == current_user.id).first()
    if not blog:
        raise HTTPException(status_code=404, detail="Blog not found")
    return blog

# Update Blog (for current user)
@router.put("/{blog_id}", response_model=BlogOut)
def update_blog(blog_id: int, updated_data: BlogUpdate, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    blog = db.query(Blog).filter(Blog.id == blog_id, Blog.owner_id == current_user.id).first()
    if not blog:
        raise HTTPException(status_code=404, detail="Blog not found")

    # Only update fields that were provided
    if updated_data.title is not None:
        blog.title = updated_data.title
    if updated_data.content is not None:
        blog.content = updated_data.content

    db.commit()
    db.refresh(blog)
    return blog


# Delete Blog (for current user)
@router.delete("/{blog_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_blog(blog_id: int, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    blog = db.query(Blog).filter(Blog.id == blog_id, Blog.owner_id == current_user.id).first()
    if not blog:
        raise HTTPException(status_code=404, detail="Blog not found")

    db.delete(blog)
    db.commit()
    return {"detail": "Blog deleted successfully"}
