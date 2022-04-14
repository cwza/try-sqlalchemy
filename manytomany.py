from sqlalchemy import create_engine
from sqlalchemy import Column, Integer, String, Text, ForeignKey
from sqlalchemy.orm import sessionmaker, relationship, backref
from sqlalchemy.ext.associationproxy import association_proxy
from helper import Base

engine = create_engine('sqlite:///data.db', echo=True)
Session = sessionmaker()
Session.configure(bind=engine)
session = Session()


# many to many Post<->Keyword

class Post(Base):
    __tablename__ = 'posts'

    id = Column(Integer, primary_key=True)
    headline = Column(String(255), nullable=False)
    body = Column(Text)

    # keywords = relationship('PostKeyword', back_populates='post', cascade="all, delete, delete-orphan")
    post_keywords = relationship('PostKeyword', back_populates='post', cascade="all, delete, delete-orphan")
    keywords = association_proxy('post_keywords', 'keyword', creator=lambda keyword: PostKeyword(keyword=keyword))

    def __init__(self, headline, body):
        self.headline = headline
        self.body = body

class Keyword(Base):
    __tablename__ = 'keywords'

    id = Column(Integer, primary_key=True)
    content = Column(String(50), nullable=False, unique=True)

    # posts = relationship('PostKeyword', back_populates='keyword', cascade="all, delete, delete-orphan")
    post_keywords = relationship('PostKeyword', back_populates='keyword', cascade="all, delete, delete-orphan")
    posts = association_proxy('post_keywords', 'post')

    def __init__(self, content):
        self.content = content

class PostKeyword(Base):
    __tablename__ = 'posts_keywords'
    id = Column(Integer, primary_key = True)
    post_id = Column(Integer, ForeignKey('posts.id', ondelete="CASCADE"), index=True)
    # post = relationship("Post", foreign_keys=[post_id], backref=backref("post_keywords", cascade="all, delete, delete-orphan"))
    post = relationship("Post", foreign_keys=[post_id], back_populates="post_keywords")
    keyword_id = Column(Integer, ForeignKey('keywords.id', ondelete='CASCADE'), index=True)
    # keyword = relationship("Keyword", foreign_keys=[keyword_id], backref=backref("post_keywords", cascade="all, delete, delete-orphan"))
    keyword = relationship("Keyword", foreign_keys=[keyword_id], back_populates="post_keywords")

with engine.connect() as con:
    con.execute("drop table if exists posts_keywords;")
    con.execute("drop table if exists keywords")
    con.execute("drop table if exists posts")
print(repr(Base.metadata.create_all(engine)))


post = Post("Wendy's Blog Post", "This is a test")
post.keywords = [Keyword('wendy'), Keyword('firstpost')]
session.add(post)
session.commit()

post = session.query(Post).filter_by(headline="Wendy's Blog Post").one()
print(f"xxxxxxxxx: {post.keywords}")
session.delete(post)
session.commit()