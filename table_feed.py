from database import Base, SessionLocal
from sqlalchemy import Column, Integer, String,TIMESTAMP, func, ForeignKey
from sqlalchemy.orm import relationship
from table_post import Post
from table_user import User


# SQLALCHEMY_DATABASE_URL = "sqlite:///./sql_app.db"
# NOTE be careful when sharing
SQLALCHEMY_DATABASE_URL = "postgresql://username:password@localhost/database"

class Feed(Base):
    __tablename__ = "feed_action"
    user_id = Column(Integer, ForeignKey(User.id), primary_key=True, index=True)
    post_id = Column(Integer, ForeignKey(Post.id), primary_key=True, index=True)
    action = Column(String)
    time = Column(TIMESTAMP)
    user = relationship("User")
    post = relationship("Post")



