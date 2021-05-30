import datetime
import os
import json
import random
import requests

from flask_login import login_required, current_user
from flask import Blueprint, render_template, redirect, url_for, flash, send_from_directory, make_response
from flask import request, Response

from vocabulizer.settings import api_version, wordnik_api_key, spc_wrdnk_pos_dict, READING_TEXTS_TOP_LIMIT
from vocabulizer.pipelines import used_vocabulary, lemma
from vocabulizer.models import UserVocabulary, Word, VocabularyEntry, TenseChallengeItem, Article, \
    UserArticlePreference, UserTensesChallengePreference, FactChallenge, Challenge, LanguageSkills, ItemTypes
from vocabulizer import db

from supermemo2 import SMTwo

main = Blueprint('main', __name__, static_folder='build/', static_url_path='/vocabulizer-frontend')


@main.route('/')
def index():
    return render_template('index.html')


@main.route('/profile')
@login_required
def profile():
    return render_template('profile.html', name=current_user.name)


@main.route('/reader')
def reader():
    return main.send_static_file('index.html')


@main.route("/get-dictionary-from-src", methods=['POST'])
@main.route("/api/{}/get-dictionary-from-src".format(api_version), methods=['POST'])
@login_required
def get_dictionary_from_src():
    src = request.json["src"]
    user_vocabulary = UserVocabulary.query.filter_by(user_id=current_user.id).first()
    return Response(json.dumps({
        "data": {"words": [
            {
                "dictionaryWord": k[0],
                "partOfSpeechTag": k[1],
                "languages": ["en"],
                "known": VocabularyEntry.query.filter_by(vocab=user_vocabulary,
                                                         word=Word.query.filter_by(text=k[0], pos=k[1]).
                                                         first()).first() is not None
                }
            for k, v in used_vocabulary(src).items()
            ]
            },
        "error": None,
        "meta": {
            "entries": [
                {
                    "word": k[0],
                    "entries": [{"start": entry[0], "end": entry[0] + entry[1]} for entry in v]
                    }
                for k, v in used_vocabulary(src).items()
                ]
            }
        }), content_type="application/json")


@main.route("/word/<word>/definitions", methods=["GET"])
def get_word_definitions(word):
    pos_tag = request.args.get("pos")

    definitions_params = {
        "limit": 200,
        "includeRelated": False, "useCanonical": False,
        "includeTags": False, "api_key": wordnik_api_key,
        }

    if spc_wrdnk_pos_dict.get(pos_tag, None) is not None:
        definitions_params["partOfSpeech"] = spc_wrdnk_pos_dict[pos_tag]

    words_definitions_r = requests.get(
        "https://api.wordnik.com/v4/word.json/{}/definitions".format(word),
        params=definitions_params
        )

    return Response(json.dumps(words_definitions_r.json()),
                    content_type="application/json")


@main.route('/add-known-word', methods=['POST'])
@login_required
def add_known_word():
    challenge = Challenge.query.filter_by(name="reading").first()
    lang_skill = LanguageSkills.query.filter_by(name="vocabulary").first()
    item_type = ItemTypes.query.filter_by(name="word").first()

    word = request.json["dictionaryWord"]
    pos = request.json["partOfSpeechTag"]
    source = request.json["source"]
    print((word, pos, source))

    word_obj = Word.query.filter_by(text=word, pos=pos).first()

    if word_obj is None:
        word_obj = Word(text=word, pos=pos)
        db.session.add(word_obj)
        db.session.commit()

    user_vocabulary = UserVocabulary.query.filter_by(user_id=current_user.id).first()
    vocab_entry = VocabularyEntry.query.filter_by(vocab=user_vocabulary, word_id=word_obj.id, word=word_obj).first()

    fact_challenge = FactChallenge(user_id=current_user.id, challenge_id=challenge.id,
                                   skill_id=lang_skill.id, item_type_id = item_type.id, item_id=word_obj.id,
                                   quality=1,
                                   challenge_time=datetime.datetime.now())
    db.session.add(fact_challenge)

    if vocab_entry is None:
        vocab_entry = VocabularyEntry(vocab=user_vocabulary, vocab_id=user_vocabulary.id, word_id=word_obj.id,
                                      word=word_obj, known_before=True)
        db.session.add(vocab_entry)
        db.session.commit()

    # source = request.form.get["source"]

    return Response("Wow! Such a vocabulary! Much words!")


@main.route("/add-to-memorise", methods=["POST"])
@login_required
def add_to_memorise():
    challenge = Challenge.query.filter_by(name="reading").first()
    lang_skill = LanguageSkills.query.filter_by(name="vocabulary").first()
    item_type = ItemTypes.query.filter_by(name="word").first()

    word = request.json["dictionaryWord"]
    pos = request.json["partOfSpeechTag"]
    # source = request.json["source"]
    word_obj = Word.query.filter_by(text=word, pos=pos).first()

    if word_obj is None:
        word_obj = Word(text=word, pos=pos)
        db.session.add(word_obj)
        db.session.commit()

    user_vocabulary = UserVocabulary.query.filter_by(user_id=current_user.id).first()
    vocab_entry = VocabularyEntry.query.filter_by(vocab=user_vocabulary, word_id=word_obj.id, word=word_obj).first()

    fact_challenge = FactChallenge(user_id=current_user.id, challenge_id=challenge.id,
                                   skill_id=lang_skill.id, item_type_id = item_type.id, item_id=word_obj.id,
                                   quality=0,
                                   challenge_time=datetime.datetime.now())
    db.session.add(fact_challenge)

    if vocab_entry is None:
        vocab_entry = VocabularyEntry(vocab=user_vocabulary, vocab_id=user_vocabulary.id, word_id=word_obj.id,
                                      word=word_obj, next_review=datetime.datetime.now(), known_before=False)
        db.session.add(vocab_entry)
        db.session.commit()

    # source = request.form.get["source"]

    return Response("Wow! Such a vocabulary! Much words!")


@main.route("/text-to-read", methods=["GET"])
@login_required
def text_to_read():
    articles_preference = UserArticlePreference.query.filter_by(user_id=current_user.id).\
        order_by(UserArticlePreference.novelty).limit(READING_TEXTS_TOP_LIMIT).all()
    article_id = sorted([(pref.interest, pref.article_id) for pref in articles_preference], key=lambda x: x[0],
                        reverse=True)[0][1]
    article = Article.query.filter_by(id=article_id).first()
    return {
        "src": article.title + article.body
        }


@main.route("/flashcard_challenge", methods=["GET"])
@login_required
def flashcard_question():
    user_vocabulary = UserVocabulary.query.filter_by(user_id=current_user.id).first()
    vocab_entry = VocabularyEntry.query.filter_by(vocab=user_vocabulary,
                                                  known_before=False).order_by(VocabularyEntry.next_review).first()

    definitions_params = {"limit": 5, "includeRelated": False, "useCanonical": False,
                          "includeTags": False, "api_key": wordnik_api_key}

    examples_params = {"limit": 2, "includeDuplicates": False, "useCanonical": False, "api_key": wordnik_api_key}

    # if spc_wrdnk_pos_dict.get(vocab_entry.word.pos, None) is not None:
    #     definitions_params["partOfSpeech"] = spc_wrdnk_pos_dict[vocab_entry.word.pos]

    words_definitions_r = requests.get(
        "https://api.wordnik.com/v4/word.json/{}/definitions".format(vocab_entry.word.text),
        params=definitions_params)

    words_examples_r = requests.get(
        "https://api.wordnik.com/v4/word.json/{}/examples".format(vocab_entry.word.text),
        params=examples_params
        )

    definitions_list = [{"pos": definition["partOfSpeech"], "text": definition["text"].replace("<xref>", "").replace("</xref>", "")}
                        for definition in words_definitions_r.json() if "text" in definition and "partOfSpeech" in
                        definition]

    examples_list = [{"title": example["title"],
                      "text":example["text"].replace(vocab_entry.word.text,
                                                     "{}".format(vocab_entry.word.text))}
                     for example in words_examples_r.json()["examples"] if "title" in example and "text" in example]

    return render_template("flashcard.html",
                           word=vocab_entry.word.text + " ({})".format(vocab_entry.word.pos),
                           word_id=vocab_entry.word_id,
                           definitions=definitions_list,
                           examples=examples_list)


@main.route("/flashcard_answer", methods=["POST"])
@login_required
def flashcard_answer():
    challenge = Challenge.query.filter_by(name="flashcard").first()
    lang_skill = LanguageSkills.query.filter_by(name="vocabulary").first()
    item_type = ItemTypes.query.filter_by(name="word").first()

    word_id = request.form["word_id"]
    quality = 5 if request.form["remember"] else 0
    user_vocabulary = UserVocabulary.query.filter_by(user_id=current_user.id).first()
    vocab_entry = VocabularyEntry.query.filter_by(vocab=user_vocabulary, word_id=word_id).first()

    fact_challenge = FactChallenge(user_id=current_user.id, challenge_id=challenge.id,
                                   skill_id=lang_skill.id, item_type_id = item_type.id, item_id=word_id,
                                   quality=quality,
                                   challenge_time=datetime.datetime.now())
    db.session.add(fact_challenge)

    if vocab_entry.easiness is not None:
        r = SMTwo(vocab_entry.easiness,
                  vocab_entry.interval,
                  vocab_entry.repetitions).review(quality, datetime.datetime.now().strftime("%Y-%m-%d"))
    else:
        r = SMTwo.first_review(quality, datetime.datetime.now().strftime("%Y-%m-%d"))
    vocab_entry.easiness = r.easiness
    vocab_entry.interval = r.interval
    vocab_entry.repetitions = r.repetitions
    vocab_entry.next_review = r.review_date
    # db.session.add(vocab_entry)
    db.session.commit()
    return redirect(url_for('main.flashcard_question'))


@main.route("/tenses_challenge", methods=["GET"])
@login_required
def tenses_question():
    user_items_preferences = UserTensesChallengePreference.query.filter_by(passed=False,
                                                                           user_id=current_user.id).\
        order_by(UserTensesChallengePreference.complexity).limit(5).all()
    items = [TenseChallengeItem.query.filter_by(id=pref.item_id).first() for pref in user_items_preferences]
    items = [{"question": item.question, "hint": lemma(item.answer), "answer": item.answer,
              "id": item.id} for item in items]

    return render_template("tense_question.html", items=items)


@main.route("/tenses_answer", methods=["POST"])
@login_required
def tenses_answer():
    results = []
    challenge = Challenge.query.filter_by(name="tenses").first()
    lang_skill = LanguageSkills.query.filter_by(name="grammar").first()
    item_type = ItemTypes.query.filter_by(name="put_in_word_excercise").first()

    for item_id in request.form:
        item = TenseChallengeItem.query.filter_by(id=item_id).first()
        results.append({"correct": item.answer == request.form[item_id].lower().rstrip().lstrip(),
                        "question": item.question,
                        "answer": item.answer,
                        "user_answer": request.form[item_id]})
        fact_challenge = FactChallenge(user_id=current_user.id, challenge_id=challenge.id,
                                       skill_id=lang_skill.id, item_type_id = item_type.id, item_id=item.id,
                                       quality=float(item.answer == request.form[item_id].lower().rstrip().lstrip()),
                                       challenge_time=datetime.datetime.now())
        db.session.add(fact_challenge)

        if item.answer == request.form[item_id]:
            user_item_preference = UserTensesChallengePreference.query.filter_by(user_id=current_user.id,
                                                                                 item_id=item_id).first()
            user_item_preference.passed = True

    db.session.commit()

    return render_template("tense_answer.html", results=results)


@main.route("/update_tense_challenge_items")
def update_tense_challenge_items():
    TenseChallengeItem.update_tense_challenge_items(db)
    UserTensesChallengePreference.compute_preferences(db)
    return "updated successfully"


@main.route("/update_articles_from_files")
def update_article_from_files():
    Article.update_articles_from_files(db)
    UserArticlePreference.compute_novelty(db)
    UserArticlePreference.compute_interest(db)
    return "updated successfully"


@main.route("/update_recommendations")
def update_recommendations():
    UserArticlePreference.compute_interest(db)
    return "updated successfully"


@main.route("/update_complexity")
def update_complexity():
    UserTensesChallengePreference.compute_preferences(db)
    UserArticlePreference.compute_novelty(db)
    return "updated successfully"
