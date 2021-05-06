from flask_login import UserMixin
from datetime import datetime
from . import db


class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(100), unique=True)
    password = db.Column(db.String(100))
    name = db.Column(db.String(1000))


class UserVocabulary(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    user = db.relationship('User', backref=db.backref('vocabulary', lazy=True))
    language = db.Column(db.String)


class VocabularyEntry(db.Model):
    __tablename__ = 'vocabulary_entry'
    id = db.Column(db.Integer, primary_key=True)
    vocab_id = db.Column(db.Integer, db.ForeignKey("user_vocabulary.id"))
    vocab = db.relationship("UserVocabulary")
    word_id = db.Column(db.Integer, db.ForeignKey("word.id"))
    word = db.relationship('Word')
    read_times = db.Column(db.Integer, default=0)
    challenged_times = db.Column(db.Integer, default=0)
    know_times = db.Column(db.Integer, default=0)
    known_before = db.Column(db.Boolean, default=False)
    last_challenged = db.Column(db.DateTime, default=None)
    created = db.Column(db.DateTime, default=datetime.utcnow)


class Word(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    pos = db.Column(db.String, index=True)
    text = db.Column(db.String, index=True)


class Article(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String, index=True)
    body = db.Column(db.String, index=True)


class UserArticlePreference(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    article_id = db.Column(db.Integer, db.ForeignKey("article.id"))
    user_id = db.Column(db.Integer, db.ForeignKey("user.id"))
    complexity = db.Column(db.Float)
    interest = db.Column(db.Float)
    new_words = db.Column(db.Integer)
