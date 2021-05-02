import unittest
import requests

from app import app
from vocabulizer.settings import wordnik_api_key, PORT, api_version


class WordnikAPI(unittest.TestCase):

    def test_wordnik_api(self):
        r = requests.get("http://api.wordnik.com/v4/words.json/randomWord",
                         params={"api_key": wordnik_api_key})
        print(r.json())
        self.assertGreater(len(r.json()["word"]), 0)

    def test_wordnik_definitions(self):
        r = requests.get("https://api.wordnik.com/v4/word.json/hobbedehoy/definitions",
                         params={"limit": 200,
                                 "includeRelated": False, "useCanonical": False,
                                 "includeTags": False, "api_key": wordnik_api_key})
        print(r.json())
        self.assertGreater(len(r.json()), 0)


class VocabulizerAPI(unittest.TestCase):

    def setUp(self):
        app.config['TESTING'] = True
        app.config['WTF_CSRF_ENABLED'] = False
        app.config['DEBUG'] = False
        self.app = app.test_client()
        self.assertEqual(app.debug, False)

    def tearDown(self):
        pass

    def test_api_dictionary_from_src(self):
        with open("text_sample.txt", "r", encoding="utf8") as f:
            text_sample = f.read()
        r = self.app.post("api/{}/get-dictionary-from-vocabulizer".format(api_version),
                          json={"vocabulizer": text_sample})
        self.assertEqual(r.status_code, 200)
        print(r.json)

    def test_api_words_definitions(self):
        word = "hobbedehoy"
        r = self.app.get("api/{}/{}/definitions".format(api_version, word))
        self.assertEqual(r.status_code, 200)
        print(r.json)

    def test_api_words_definitions_with_pos_tag(self):
        word = "run"
        pos_tag_1 = "NOUN"
        pos_tag_2 = "VERB"

        r_1 = self.app.get("api/{}/{}/definitions?pos={}".format(api_version, word, pos_tag_1))
        r_2 = self.app.get("api/{}/{}/definitions?pos={}".format(api_version, word, pos_tag_2))

        self.assertEqual(r_1.status_code, 200)
        self.assertEqual(r_2.status_code, 200)
        self.assertNotEqual(r_1.json, r_2.json)
        print(r_1.json)
        print(r_2.json)

    def test_api_definitions_from_src(self):
        with open("text_sample.txt", "r", encoding="utf8") as f:
            text_sample = f.read()
        r = self.app.post("api/{}/get-dictionary-from-vocabulizer".format(api_version),
                          json={"vocabulizer": text_sample})
        self.assertEqual(r.status_code, 200)
        for w in r.json["data"]["words"][:10]:
            definition_r = self.app.get("api/{}/{}/definitions?pos={}".format(api_version, w["dictionaryWord"],
                                                                              w["partOfSpeechTag"]))
            self.assertEqual(r.status_code, 200)
            print(w, definition_r.json)


if __name__ == '__main__':
    unittest.main()
