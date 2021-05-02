import json
import random
import requests

from flask_login import login_required, current_user
from flask import Blueprint, render_template
from flask import request, Response
from flask_sqlalchemy import SQLAlchemy
from .models import User

from vocabulizer.settings import api_version, wordnik_api_key, spc_wrdnk_pos_dict
from vocabulizer.pipelines import used_vocabulary

main = Blueprint('main', __name__)


@main.route('/')
def index():
    return render_template('index.html')


@main.route('/profile')
@login_required
def profile():
    return render_template('profile.html', name=current_user.name)


@main.route("/api/{}/get-dictionary-from-vocabulizer".format(api_version), methods=['POST'])
def get_dictionary_from_src():
    src = request.json["vocabulizer"]
    return Response(json.dumps({
        "data": {"words": [
            {
                # TODO: Add id
                "dictionaryWord": k[0],
                "partOfSpeechTag": k[1],
                "languages": ["en"],
                "known": random.choice([True, False])
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
    #   TODO: Return link on documentation
    return 'Hello World!'


@main.route("/api/{}/health".format(api_version))
def ping():
    return 'Hello World!'


@main.route("/api/{}/add-known-word".format(api_version), methods=['POST'])
def add_known_word():
    word = request.json["dictionaryWord"]
    pos = request.json["partOfSpeechTag"]
    source = request.json["source"]
    print((word, pos, source))
    return Response("Wow! Such a vocabulary! Much words!")