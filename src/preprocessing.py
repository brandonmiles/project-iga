# Credit: Soumyadip Sarkar (from kaggle.com)
import numpy as np
import nltk
import re
from nltk.corpus import stopwords
from gensim.models import Word2Vec


# Convert essay into a list of words
def essay_to_wordlist(essay_v, remove_stopwords):
    essay_v = re.sub("[^a-zA-Z]", " ", essay_v)
    words = essay_v.lower().split()
    if remove_stopwords:
        stops = set(stopwords.words("english"))
        words = [w for w in words if w not in stops]
    return words


# Convert essay into a list of sentences
def essay_to_sentences(essay_v, remove_stopwords):
    tokenizer = nltk.data.load('tokenizers/punkt/english.pickle')
    raw_sentences = tokenizer.tokenize(essay_v.strip())
    sentences = []
    for raw_sentence in raw_sentences:
        if len(raw_sentence) > 0:
            sentences.append(essay_to_wordlist(raw_sentence, remove_stopwords))
    return sentences


# This function computes the feature vector given some words from
# an essay. An explanation of what a feature is may be found here:
# https://en.wikipedia.org/wiki/Feature_(machine_learning).
def make_feature_vec(words, model, num_features):
    feature_vec = np.zeros((num_features,), dtype="float32")
    num_words = 0
    index2word_set = set(model.wv.index2word)
    for word in words:
        if word in index2word_set:
            num_words += 1
            feature_vec = np.add(feature_vec, model[word])
    feature_vec = np.divide(feature_vec, num_words)
    return feature_vec


# This function computes the feature vector for each essay and
# stores them in another vector called 'essay_feature_vecs'.
def get_avg_feature_vecs(essays, model, num_features):
    counter = 0
    essay_feature_vecs = np.zeros((len(essays), num_features), dtype="float32")
    for essay in essays:
        essay_feature_vecs[counter] = make_feature_vec(essay, model, num_features)
        counter += 1
    return essay_feature_vecs
