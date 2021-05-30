import os
import json

root_path = os.path.dirname(os.path.join(__file__))
secrets_path = os.path.join(root_path, "secrets")
dictionaries_path = os.path.join(root_path, "dictionaries")
texts_path = os.path.join(root_path, "texts")
api_version = "v0"

DAYS_BEFORE_FORGETTING_THRESHOLD = 60
READING_TEXTS_TOP_LIMIT = 100

with open(os.path.join(secrets_path, "wordnik.json"), 'r') as f:
    wordnik_api_key = json.load(f)["API_KEY"]

with open(os.path.join(dictionaries_path, "spacy_wordnik_pos_tags.json"), "r") as f:
    spc_wrdnk_pos_dict = json.load(f)

PORT = 80
DATABASE_URI = 'postgresql+psycopg2://vocabulizer:TdHCTWU12ywK0fZ1Wpc0@localhost:5432/vocabulizer'
