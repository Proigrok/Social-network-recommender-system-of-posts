from database import Base, SessionLocal
from sqlalchemy import Column, Integer, String


# SQLALCHEMY_DATABASE_URL = "sqlite:///./sql_app.db"
# NOTE be careful when sharing
SQLALCHEMY_DATABASE_URL = "postgresql://username:password@localhost/database"

class Post(Base):
    __tablename__ = "post"
    id = Column(Integer, primary_key=True)
    text = Column(String)
    topic = Column(String)

if __name__ == "__main__":
    session = SessionLocal()
    k = session.query(Post.id).filter(Post.topic == "business").order_by(Post.id.desc()).limit(10).all()

    print([id[0] for id in k])




