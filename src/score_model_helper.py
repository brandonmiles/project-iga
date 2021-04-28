from keras.preprocessing.sequence import pad_sequences
from nltk.tokenize import word_tokenize
import numpy as np
import pandas as pd
import pickle
import preprocessing


def get_dataframe(data_loc):
    """
    Returns pandas DataFrame for given file

    Parameters
    ----------
    data_loc : str
        Filepath of data file

    Returns
    -------
    df : pandas.DataFrame
        The corresponding DataFrame
    """
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


def get_clean_essays(essays):
    """
    Preprocesses each essay into a list of words. This allows the essay to be 
    sequentially processed by the model word-by-word.

    Parameters
    ----------
    essays : list of str
        The list of essays we want to convert

    Returns
    -------
    clean_essays : list of list of str
        A list of essays, where each essay is a list of words
    """
    clean_essays = []
    for essay_v in essays:
        clean_essays.append(preprocessing.essay_to_wordlist(essay_v, remove_stopwords=True))
    return clean_essays


def preprocess(text_raw, tk):
    """
    This preprocessing step is for the evaluation function. The procedure first
    tokenizes the essay. Then, it transforms the tokens into a sequence of integers.
    Finally, it pads the sequence with additional characters so that each essay will
    have the same sequence length.
    Credit: yetianpro on GitHub

    Parameters
    ----------
    text_raw : str
        The raw essay
    tk : Tokenizer
        A tokenizer from the Keras preprocessing package

    Returns
    -------
    text_array : list of int
        A list of integers representing the words in the essay
    """
    text_tokenized = word_tokenize(text_raw)
    text_encoded = tk.texts_to_sequences([text_tokenized])
    text_array = pad_sequences(text_encoded, maxlen=200, padding='post')
    return text_array