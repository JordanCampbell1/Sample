from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from schemas import BlogCreate
from models import Blog
from typing import List
from database import get_db

router = APIRouter(prefix="/blog")

@router.post("/")
def create_blog(blog: BlogCreate, db: Session = Depends(get_db)):
    new_blog = Blog(title=blog.title, content=blog.content, owner_id=1)  # for demo, static owner
    db.add(new_blog)
    db.commit()
    db.refresh(new_blog)
    return new_blog

@router.get("/", response_model=List[BlogCreate])
def get_blogs(db: Session = Depends(get_db)):
    return db.query(Blog).all()
