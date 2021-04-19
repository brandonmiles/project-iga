from keras.preprocessing.sequence import pad_sequences
from nltk.tokenize import word_tokenize
import numpy as np
import pandas as pd
import pickle
import preprocessing


# Returns pandas dataframe after getting rid of the essays we aren't grading against, also gets rid of unused columns
def get_dataframe(data_loc):
    try:
        df = pd.read_csv(data_loc, sep='\t', encoding='ISO-8859-1')
    except FileNotFoundError:
        raise FileNotFoundError(str(data_loc) + " not found")

    df = df.drop(columns=['rater1_domain1', 'rater2_domain1', 'rater3_domain1', 'rater1_domain2',
                          'domain2_score', 'rater1_trait1', 'rater1_trait2', 'rater1_trait3', 'rater1_trait4',
                          'rater1_trait5', 'rater1_trait6', 'rater2_trait1', 'rater2_trait2', 'rater2_trait3',
                          'rater2_trait4', 'rater2_trait5', 'rater2_trait6', 'rater3_trait1', 'rater3_trait2',
                          'rater3_trait3', 'rater3_trait4', 'rater3_trait5', 'rater3_trait6'])

    return df


# Preprocesses each essays into a word list (where each element of
# the list is a word). This allows the essay to be sequentially
# processed by the model word-by-word.
def get_clean_essays(essays):
    clean_essays = []
    for essay_v in essays:
        clean_essays.append(preprocessing.essay_to_wordlist(essay_v, remove_stopwords=True))
    return clean_essays


# Grabs every sentence from each essay in 'essays' and jams
# them into one array
def get_sentences(essays):
    sentences = []
    for essay in essays:
        sentences += preprocessing.essay_to_sentences(essay, remove_stopwords=True)
    return sentences


# Turns 'data_vecs' into a np array and then reshapes it into the
# proper shape for LSTM's input
def array_and_reshape(data_vecs):
    data_vecs = np.array(data_vecs)
    data_vecs = np.reshape(data_vecs, (data_vecs.shape[0], 1, data_vecs.shape[1]))
    return data_vecs


# A tokenizer is needed for evaluating an essay. Each essay is split
# into its constituent tokens, which might represent organizations, dates,
# numbers, and so on.
# 
# TODO: Remove? Possibly obsolete.
def load_tokenizer():
    with open('tokenizer/tokenizer.pickle', 'rb') as handle:
        tokenizer = pickle.load(handle)
    return tokenizer


# This preprocessing step is for the evaluation function. The procedure first
# tokenizes the essay. Then, it transforms the tokens into a sequence of integers.
# Finally, it pads the sequence with additional characters so that each essay will
# have the same sequence length. 
# Credit: yetianpro on GitHub
def preprocess(text_raw, tk):
    text_tokenized = word_tokenize(text_raw)
    text_encoded = tk.texts_to_sequences([text_tokenized])
    text_array = pad_sequences(text_encoded, maxlen=200, padding='post')
    return text_array
