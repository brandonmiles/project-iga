from keras.preprocessing.sequence import pad_sequences
from nltk.tokenize import word_tokenize
import numpy as np
import pandas as pd
import pickle
import preprocessing


# Returns pandas dataframe, with some dropped columns that
# are irrelevant for now
def get_dataframe(data_loc):
    df = pd.read_csv(data_loc, sep='\t', encoding='ISO-8859-1')
    df = df.dropna(axis=1)  # Drop columns with 'missing' values
    df = df.drop(columns=['rater1_domain1', 'rater2_domain1'])
    df = df.drop(columns=['essay_id', 'essay_set'])
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
    text_array = pad_sequences(text_encoded, maxlen=300, padding='post')
    return text_array