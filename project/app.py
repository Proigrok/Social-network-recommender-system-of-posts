from typing import List

from fastapi import Depends, FastAPI, HTTPException
from sqlalchemy.orm import Session

from database import SessionLocal

from table_user import User
from table_post import Post
from table_feed import Feed

from schema import UserGet, PostGet, FeedGet
app = FastAPI()

def get_db():
    with SessionLocal() as db:
        return db

@app.get("/user/{id}", response_model=UserGet)
def get_user(id:int, db: Session = Depends(get_db)):
    result = db.query(User).filter(User.id == id).first()
    if not result:
        raise HTTPException(404, "post not found")
    else:
        return result
@app.get("/post/{id}", response_model=PostGet)
def get_post(id:int, db: Session = Depends(get_db)):
    result = db.query(Post).filter(Post.id == id).first()
    if not result:
        raise HTTPException(404, "post not found")
    else:
        return result

@app.get("/user/{id}/feed", response_model=List[FeedGet])
def get_user_feed(id:int, limit: int = 10, db: Session = Depends(get_db)):
    return db.query(Feed).filter(Feed.user_id == id).order_by(Feed.time.desc()).limit(limit).all()

@app.get("/post/{id}/feed", response_model=List[FeedGet])
def get_post_feed(id:int, limit: int = 10, db: Session = Depends(get_db)):
    return db.query(Feed).filter(Feed.post_id == id).order_by(Feed.time.desc()).limit(limit).all()


