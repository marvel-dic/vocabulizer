import os
import json
import random
import requests

from flask_login import login_required, current_user
from flask import Blueprint, render_template, redirect, url_for, flash, send_from_directory
from flask import request, Response

from vocabulizer.settings import api_version, wordnik_api_key, spc_wrdnk_pos_dict
from vocabulizer.pipelines import used_vocabulary
from vocabulizer.models import UserVocabulary, Word, VocabularyEntry
from vocabulizer import db

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

    if vocab_entry is None:
        vocab_entry = VocabularyEntry(vocab=user_vocabulary, vocab_id=user_vocabulary.id, word_id=word_obj.id,
                                      word=word_obj, read_times=1, know_times=1, known_before=True)
        db.session.add(vocab_entry)
        db.session.commit()

    # source = request.form.get["source"]

    return Response("Wow! Such a vocabulary! Much words!")


@main.route("/add-to-memorise", methods=["POST"])
@login_required
def add_to_memorise():
    word = request.json["dictionaryWord"]
    pos = request.json["partOfSpeechTag"]
    source = request.json["source"]
    word_obj = Word.query.filter_by(text=word, pos=pos).first()

    if word_obj is None:
        word_obj = Word(text=word, pos=pos)
        db.session.add(word_obj)
        db.session.commit()

    user_vocabulary = UserVocabulary.query.filter_by(user_id=current_user.id).first()
    vocab_entry = VocabularyEntry.query.filter_by(vocab=user_vocabulary, word_id=word_obj.id, word=word_obj).first()

    if vocab_entry is None:
        vocab_entry = VocabularyEntry(vocab=user_vocabulary, vocab_id=user_vocabulary.id, word_id=word_obj.id,
                                      word=word_obj, read_times=1, know_times=0, known_before=False)
        db.session.add(vocab_entry)
        db.session.commit()

    # source = request.form.get["source"]

    return Response("Wow! Such a vocabulary! Much words!")


@main.route("/text-to-read", methods=["GET"])
def text_to_read():
    return {
        "src": "Hi! Please insert here text so you could learn new words from it!",
        }


@main.route("/flash-card-trainer", methods=["GET"])
def flash_card_trainer():
    pass
