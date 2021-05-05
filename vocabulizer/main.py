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


# @main.route('/vocabulizer-frontend/<path:path>')
# def send_js(path):
#     return redirect(url_for('static', filename="static/"+path.lstrip('static/')))
#
#
# @main.route('/vocabulizer-frontend/<filename>')
# def send_static(filename):
#     return redirect(url_for('static', filename=filename))


@main.route('/profile')
@login_required
def profile():
    return render_template('profile.html', name=current_user.name)


# @main.route('/add-known-word')
# @login_required
# def add_known_word():
#     return render_template('add_known_word.html')


@main.route('/reader')
def reader():
    return main.send_static_file('index.html')


# @main.route("/add-known-word", methods=['POST'])
# @login_required
# def form_add_known_word():
#     word = request.form.get("word")
#     pos = request.form.get("pos")
#     print(current_user.id, word, pos)
#
#     word_obj = Word.query.filter_by(text=word, pos=pos).first()
#
#     if word_obj is None:
#         word_obj = Word(text=word, pos=pos)
#         db.session.add(word_obj)
#         db.session.commit()
#
#     user_vocabulary = UserVocabulary.query.filter_by(user_id=current_user.id).first()
#     vocab_entry = VocabularyEntry.query.filter_by(vocab=user_vocabulary, word_id=word_obj.id, word=word_obj).first()
#
#     if vocab_entry is None:
#         vocab_entry = VocabularyEntry(vocab=user_vocabulary, vocab_id=user_vocabulary.id, word_id=word_obj.id,
#                                       word=word_obj, read_times=1, know_times=1, known_before=True)
#         db.session.add(vocab_entry)
#         db.session.commit()
#     else:
#         flash('YOU ALREADY ADDED THIS WORD PUNK!')
#         return redirect(url_for('main.add_known_word'))
#
#     # source = request.form.get["source"]
#
#     return redirect(url_for('main.add_known_word'))

@main.route("/get-dictionary-from-src".format(api_version), methods=['POST'])
@main.route("/api/{}/get-dictionary-from-src".format(api_version), methods=['POST'])
@login_required
def get_dictionary_from_src():
    src = request.json["src"]
    user_vocabulary = UserVocabulary.query.filter_by(user_id=current_user.id).first()
    return Response(json.dumps({
        "data": {"words": [
            {
                # TODO: Add id
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
                    # TODO: Make unique dictionary identifiers for words with the same spelling
                    "word": k[0],
                    "entries": [{"start": entry[0], "end": entry[0] + entry[1]} for entry in v]
                    }
                for k, v in used_vocabulary(src).items()
                ]
            }
        }), content_type="application/json")


# TODO: add endpoint for word definitions
@main.route("/api/{}/<word>/definitions".format(api_version), methods=["GET"])
# @main.route("/api/{}/<word>/<pos>/definitions")
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


@main.route('/api/{}/'.format(api_version))
def hello():
    """Return a friendly HTTP greeting."""
    #   TODO: Return lin
    #    k on documentation
    return 'Hello World!'


@main.route("/api/{}/health".format(api_version))
def ping():
    return 'Hello World!'


@main.route('/add-known-word', methods=['POST'])
@main.route("/api/{}/add-known-word".format(api_version), methods=['POST'])
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

    # return redirect(url_for('main.add_known_word'))

    # source = request.form.get["source"]
    return Response("Wow! Such a vocabulary! Much words!")
