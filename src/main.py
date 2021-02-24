import nltk
import pandas
import spellcheck

spell = spellcheck.SpellCheck('../data/exceptions.txt')

try:
    data = pandas.read_csv('../data/test_set.tsv', sep='\t')
    # table column names are "essay_id", "essay_set", "essay", "domain1_predictionid", "domain2_predictionid"

    token = nltk.word_tokenize(data["essay"][0])  # Reading the first essay
    number, errors = spell.number_of_errors(token)
    print(number)
    print(errors)
except FileNotFoundError:
    print("File does not exist")
