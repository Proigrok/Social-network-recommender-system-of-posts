from fastapi import Depends, FastAPI, HTTPException
from sqlalchemy.orm import Session

from database import SessionLocal

from table_user import User
from table_post import Post
from schema import UserGet, PostGet
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

