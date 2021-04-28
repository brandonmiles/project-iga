# Partial credit: Soumyadip Sarkar (from kaggle.com)
import numpy as np
import nltk
import re
from nltk.corpus import stopwords
from gensim.models import Word2Vec


def essay_to_wordlist(essay_v, remove_stopwords):
    """
    Converts given essay into a list of words, with some "stopwords"
    being removed if required

    Parameters
    ----------
    essay_v : str
        An essay to be converted to a list of words
    remove_stopwords : bool
        If True, remove stopwords from the essay

    Returns
    -------
    words : list of str
        List of words that make up the essay
    """
    essay_v = re.sub("[^a-zA-Z]", " ", essay_v)
    words = essay_v.lower().split()
    if remove_stopwords:
        stops = set(stopwords.words("english"))
        words = [w for w in words if w not in stops]
    return words


def essay_to_sentences(essay_v, remove_stopwords):
    """
    Converts given essay into a list of sentences, with some "stopwords"
    being removed if required

    Parameters
    ----------
    essay_v : str
        An essay to be converted to a list of sentences
    remove_stopwords : bool
        If True, remove stopwords from the essay

    Returns
    -------
    sentences : list of str
        List of sentences that make up the essay
    """
    tokenizer = nltk.data.load('tokenizers/punkt/english.pickle')
    raw_sentences = tokenizer.tokenize(essay_v.strip())
    sentences = []
    for raw_sentence in raw_sentences:
        if len(raw_sentence) > 0:
            sentences.append(essay_to_wordlist(raw_sentence, remove_stopwords))
    return sentences