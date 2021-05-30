import random
from sqlalchemy import and_, or_, not_

import numpy as np
import pandas as pd
import os

from flask_login import UserMixin
from datetime import datetime, timedelta
from . import db
from .pipelines import new_words_complexity, novelty_coefficient, used_vocabulary
from .settings import texts_path, DAYS_BEFORE_FORGETTING_THRESHOLD
from sklearn.metrics.pairwise import cosine_similarity


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
    easiness = db.Column(db.Float, default=None)
    repetitions = db.Column(db.Integer, default=None)
    interval = db.Column(db.Integer, default=None)
    known_before = db.Column(db.Boolean, default=False)
    last_challenged = db.Column(db.DateTime, default=None)
    next_review = db.Column(db.DateTime, default=None)
    created = db.Column(db.DateTime, default=datetime.utcnow)


class Word(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    pos = db.Column(db.String, index=True)
    text = db.Column(db.String, index=True)


class Article(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String, index=True)
    body = db.Column(db.String, index=True)

    @staticmethod
    def update_articles_from_files(db):
        for file in os.listdir(os.path.join(texts_path, "articles")):
            with open(os.path.join(texts_path, "articles", file)) as f:
                title = f.readline().rstrip()
                body = f.read()
                article = Article.query.filter_by(title=title, body=body).first()
                if article is None:
                    article = Article(title=title, body=body)
                    db.session.add(article)

            for word in used_vocabulary(title + " " + body).keys():
                    word_obj = Word.query.filter_by(text=word[1], pos=word[0]).first()

                    if word_obj is None:
                        word_obj = Word(text=word[1], pos=word[0])
                        db.session.add(word_obj)

            db.session.commit()


class UserArticlePreference(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    article_id = db.Column(db.Integer, db.ForeignKey("article.id"), index=True)
    user_id = db.Column(db.Integer, db.ForeignKey("user.id"), index=True)
    complexity = db.Column(db.Float)
    novelty = db.Column(db.Float, index=True)
    interest = db.Column(db.Float)
    new_words = db.Column(db.Integer)
    read = db.Column(db.Boolean, default=False, index=True)

    @staticmethod
    def compute_novelty(db):
        for user in User.query.all():
            user_vocabulary = UserVocabulary.query.filter_by(user=user).first()
            known_user_words = [(entry.word.text, entry.word.pos) for entry in
                                VocabularyEntry.query.filter_by(vocab_id=user_vocabulary.id).all()]
            for article in Article.query.all():
                preference = UserArticlePreference.query.filter_by(user_id=user.id,
                                                                   article_id=article.id).first()
                if preference is None:
                    preference = UserArticlePreference(user_id=user.id,
                                                       article_id=article.id,
                                                       complexity=new_words_complexity(article.title + article.body,
                                                                                       known_user_words),
                                                       novelty=novelty_coefficient(
                                                           article.title + article.body,
                                                           known_user_words)
                                                       )
                    db.session.add(preference)
                else:
                    preference.complexity = new_words_complexity(article.title + article.body,
                                                                 known_user_words)
                    preference.novelty = novelty_coefficient(article.title + article.body,
                                                             known_user_words)
        db.session.commit()

    @staticmethod
    def compute_interest(db):
        words = Word.query.all()
        users = User.query.all()
        articles = Article.query.all()

        super_user_id = -1

        user_words_interest = pd.DataFrame([[0] * len(words)]*(len(users)+1),
                                           columns=[word.id for word in words],
                                           index=[user.id for user in users] + [super_user_id]
                                           )
        user_words_interest.loc[super_user_id] = 1

        user_articles_interest = pd.DataFrame([[0] * len(articles)]*len(users),
                                              columns=[article.id for article in articles],
                                              index=[user.id for user in users]
                                              )

        for user in users:
            user_vocabulary = UserVocabulary.query.filter_by(user=user).first()

            for entry in VocabularyEntry.query.filter_by(vocab_id=user_vocabulary.id).filter(
                    or_(VocabularyEntry.next_review >= datetime.now() + timedelta(
                        days=DAYS_BEFORE_FORGETTING_THRESHOLD),
                    VocabularyEntry.known_before)).all():
                user_words_interest.loc[user.id, entry.word_id] = 1

        iuvf = np.log(len(user_words_interest)/(user_words_interest.sum(axis=0)))
        tfiuvf = user_words_interest * iuvf
        users_similarity = cosine_similarity(tfiuvf, tfiuvf)
        for i in range(len(users_similarity)):
            users_similarity[i, i] = 1
        user_word_rating = (np.identity(users_similarity.shape[0]) *
                            (1 / users_similarity.sum(axis=1))).dot(users_similarity.dot(tfiuvf))

        for article in articles:
            article_words = pd.DataFrame([[0] * len(words)],
                                         columns=[word.id for word in words],
                                         index=[article.id]
                                         )
            for word in used_vocabulary(article.title + " " + article.body).keys():
                word_obj = Word.query.filter_by(text=word[1], pos=word[0]).first()
                article_words.loc[article.id, word_obj.id] = 1

            user_articles_interest[article.id] = ((1 - user_words_interest) * user_word_rating).dot(article_words.T)

        for user in users:
            for article in articles:
                preference = UserArticlePreference.query.filter_by(user_id=user.id,
                                                                   article_id=article.id).first()
                if preference is None:
                    preference = UserArticlePreference(user_id=user.id,
                                                       article_id=article.id,
                                                       interest=user_articles_interest.loc[user.id, article.id],
                                                       )
                    db.session.add(preference)
                else:
                    preference.interest = user_articles_interest.loc[user.id, article.id]

        db.session.commit()


class UserWordPreferences(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("user.id"))
    word_id = db.Column(db.Integer, db.ForeignKey("word.id"))
    preference = db.Column(db.Float, default=0.0)


class Challenge(db.Model):
    __tablename__ = 'dim_challenges'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String)


class TenseChallengeItem(db.Model):
    __tablename__ = 'fact_tense_challenge_items'
    id = db.Column(db.Integer, primary_key=True)
    question = db.Column(db.String)
    answer = db.Column(db.String)

    @staticmethod
    def update_tense_challenge_items(db):
        tenses_df = pd.read_csv(os.path.join(texts_path, "tenses.csv"))
        for i, r in tenses_df.iterrows():
            item = TenseChallengeItem.query.filter_by(question=r["text"], answer=r["answer"]).first()
            if item is None:
                item = TenseChallengeItem(question=r["text"], answer=r["answer"])
                db.session.add(item)
                db.session.commit()


class UserTensesChallengePreference(db.Model):
    __tablename__ = 'fact_tense_challenge_user_preference'
    id = db.Column(db.Integer, primary_key=True)
    item_id = db.Column(db.Integer, db.ForeignKey("fact_tense_challenge_items.id"))
    user_id = db.Column(db.Integer, db.ForeignKey("user.id"))
    complexity = db.Column(db.Float)
    passed = db.Column(db.Boolean, default=False)

    @staticmethod
    def compute_preferences(db):
        for user in User.query.all():
            user_vocabulary = UserVocabulary.query.filter_by(user=user).first()
            known_user_words = [(entry.word.text, entry.word.pos) for entry in
                                VocabularyEntry.query.filter_by(vocab_id=user_vocabulary.id).filter(or_(
                                    VocabularyEntry.next_review >= datetime.now() +
                                    timedelta(days=DAYS_BEFORE_FORGETTING_THRESHOLD),
                                    VocabularyEntry.known_before)).all()]
            for item in TenseChallengeItem.query.all():
                preference = UserTensesChallengePreference.query.filter_by(user_id=user.id,
                                                                           item_id=item.id).first()
                if preference is None:
                    preference = UserTensesChallengePreference(item_id=item.id, user_id=user.id,
                                                               complexity=new_words_complexity(
                                                                   item.question.format(item.answer),
                                                                   known_user_words)
                                                               )
                    db.session.add(preference)
                else:
                    preference.complexity = new_words_complexity(
                        item.question.format(item.answer),
                        known_user_words)

        db.session.commit()


class LanguageSkills(db.Model):
    __tablename__ = 'dim_lang_skills'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String)


class ItemTypes(db.Model):
    __tablename__ = 'dim_item_types'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String)


class FactChallenge(db.Model):
    __tablename__ = 'fact_challenges'
    id = db.Column(db.Integer, primary_key=True)
    challenge_id = db.Column(db.Integer, db.ForeignKey("dim_challenges.id"))
    skill_id = db.Column(db.Integer, db.ForeignKey("dim_lang_skills.id"))
    user_id = db.Column(db.Integer, db.ForeignKey("user.id"))
    item_id = db.Column(db.Integer)
    item_type_id = db.Column(db.Integer, db.ForeignKey("dim_item_types.id"))
    quality = db.Column(db.Float)
    challenge_duration = db.Column(db.Float)
    challenge_time = db.Column(db.DateTime)
