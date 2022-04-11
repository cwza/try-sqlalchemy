from sqlalchemy import create_engine
from sqlalchemy import Column, Integer, String, ForeignKey
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, relationship, selectinload
from helper import Base

engine = create_engine('sqlite:///data.db', echo=True)
Session = sessionmaker()
Session.configure(bind=engine)
session = Session()


class User(Base):
    __tablename__ = 'users'

    id = Column(Integer, primary_key=True)
    name = Column(String(50))
    fullname = Column(String(50))

    addresses = relationship("Address", back_populates="user", cascade="all, delete, delete-orphan")

    def __repr__(self):
        return f"<User(id = {self.id}, name = {self.name}, fullname = {self.fullname})>"

class Address(Base):
    __tablename__ = 'addresses'
    id = Column(Integer, primary_key=True)
    email_address = Column(String(50), nullable=False)
    user_id = Column(Integer, ForeignKey('users.id', ondelete="CASCADE"), index=True)

    user = relationship("User", back_populates="addresses")

    def __repr__(self):
        return f'<Address(id={self.id}, email_address={self.email_address})>'
    
with engine.connect() as con:
    con.execute("drop table if exists addresses")
    con.execute("drop table if exists users;")
print(repr(Base.metadata.create_all(engine)))


jack = User(name='jack', fullname='Jack Bean')
jack.addresses = [Address(email_address='jack@google.com'), Address(email_address='j25@yahoo.com')]
session.add(jack)
session.commit()

# lazy load
jack = session.query(User).filter_by(name='jack').one()
del jack.addresses[1] # load addresses now

session.delete(jack)
session.commit()

# eager load 
# jack = session.query(User).filter_by(name='jack').options(selectinload(User.addresses)).one()
