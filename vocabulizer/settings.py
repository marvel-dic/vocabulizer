import os
import json

root_path = os.path.dirname(os.path.join(__file__))
secrets_path = os.path.join(root_path, "secrets")
dictionaries_path = os.path.join(root_path, "dictionaries")
api_version = "v0"

with open(os.path.join(secrets_path, "wordnik.json"), 'r') as f:
    wordnik_api_key = json.load(f)["API_KEY"]

with open(os.path.join(dictionaries_path, "spacy_wordnik_pos_tags.json"), "r") as f:
    spc_wrdnk_pos_dict = json.load(f)

PORT = 80