from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import Column, Integer, String, Date, ForeignKey, Boolean
from sqlalchemy.orm import relationship

Base = declarative_base()


class Article(Base):
    __tablename__ = 'articles'
    id = Column(Integer, primary_key=True)
    title = Column(String)
    body = Column(String)


class User(Base):
    __tablename__ = 'users'
    id = Column(Integer, primary_key=True)
    user_name = Column(String)
    vocabularies = relationship("UserVocabulary")
    articles = relationship("Article")


class UserVocabulary(Base):
    __tablename__ = 'user_vocabulary'
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    language = Column(String)


class VocabularyEntry(Base):
    __tablename__ = 'vocabulary_entry'
    id = Column(Integer, primary_key=True)
    word_id = Column(Integer, ForeignKey("words.id"))
    read_times = Column(Integer)
    challenged_times = Column(Integer)
    know_times = Column(Integer)
    known_before = Column(Boolean)


class Word(Base):
    __tablename__ = 'words'
    id = Column(Integer, primary_key=True)
    pos = Column(String, index=True)
    text = Column(String, index=True)