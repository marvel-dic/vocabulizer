""""
This module contains functions to process text and return its features
"""
import spacy
import subprocess
import sys
import pandas as pd

nlp = spacy.load("en_core_web_sm")


def used_vocabulary(text):
    """This functions takes a text and returns the vocabulary of the unique words"""
    stop_words = [('-PRON-', 'PRON'), ('.', 'PUNCT'), (',', 'PUNCT'), ('-PRON-', 'DET'), ('-', 'PUNCT'),
                  ('"', 'PUNCT'), ('\n\n', 'SPACE'), ('’s', 'PART'), ('’', 'VERB'), ('’d', 'VERB'), (';', 'PUNCT'),
                  ('?', 'PUNCT'), ('\n\n ', 'SPACE'), ('’d', 'PUNCT'), ('\n', "SPACE")]

    doc = nlp(text)
    words = {}
    for token in doc:
        if (token.lemma_, token.pos_) in stop_words or token.is_digit or token.is_punct or token.like_num or \
                token.like_email or token.like_url or token.is_currency:
            continue
        words[(token.lemma_, token.pos_)] = words.get((token.lemma_, token.pos_), []) + [(token.idx, len(token))]
        # words[token.lemma_] = [words.get(token.lemma_, [0])[0] + 1]
        # if token.lemma_ not in words:
        #     words[token.lemma_] = {}
        # words[token.lemma_][token.pos_] = words[token.lemma_].get(token.pos_, 0) + 1

    return words


def lemma(word):
    doc = nlp(word)
    for token in doc:
        return token.lemma_


def new_words_complexity(text, known_words):
    """
    string: text
    list: known_words in format (POS, word)
    """
    used_words = used_vocabulary(text)
    return len(set(used_words.keys()).difference(set(known_words)))/len(used_words.keys())


def novelty_coefficient(text, known_words):
    """
    string: text
    list: known_words in format (POS, word)
    """
    complexity = new_words_complexity(text, known_words)
    if complexity == 0:
        return float("inf")
    return 1 / complexity * (0.2 - complexity) ** 2


if __name__ == "__main__":
    ext = ("When Sebastian Thrun started working on self-driving cars at "
           "Google in 2007, few people outside of the company took him "
           "seriously. “I can tell you very senior CEOs of major American "
           "car companies would shake my hand and turn away because I wasn’t "
           "worth talking to,” said Thrun, in an interview with Recode earlier "
           "this week.")

    print(used_vocabulary(ext))

