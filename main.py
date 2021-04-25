import datetime
import json

import requests
from flask_cors import CORS
from flask import Flask, request, Response
from settings import api_version, wordnik_api_key, spc_wrdnk_pos_dict, PORT
from pipelines import used_vocabulary

app = Flask(__name__)
cors = CORS(app, resources={r"/api/*": {"origins": "*"}})


@app.route("/api/{}/get-dictionary-from-src".format(api_version), methods=['POST'])
def get_dictionary_from_src():
    src = request.json["src"]
    return Response(json.dumps({
        "data": {"words": [
            {
                # TODO: Add id
                "dictionaryWord": k[0],
                "partOfSpeechTag": k[1],
                "languages": ["en"],
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
@app.route("/api/{}/<word>/definitions".format(api_version), methods=["GET"])
# @app.route("/api/{}/<word>/<pos>/definitions")
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


@app.route('/api/{}/'.format(api_version))
def hello():
    """Return a friendly HTTP greeting."""
    #   TODO: Return link on documentation
    return 'Hello World!'


@app.route("/api/{}/health".format(api_version))
def ping():
    return 'Hello World!'


@app.route("/")
def root():
    return "It is {} on server".format(datetime.datetime.now().strftime("%H-%M-%S"))


if __name__ == "__main__":
    app.run("127.0.0.1", port=PORT, debug=True)
