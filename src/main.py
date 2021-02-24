import pandas
import spellcheck

spell = spellcheck.SpellCheck('../data/exceptions.tsv')

try:
    data = pandas.read_csv('../data/test_set.tsv', sep='\t')
    # table column names are "essay_id", "essay_set", "essay", "domain1_predictionid", "domain2_predictionid"

    for i in range(len(data['essay'])):
        number, errors = spell.number_of_errors(data['essay'][i])
        print("Essay: ", i, " Errors: ", number)
        print(errors)
except FileNotFoundError:
    print("File does not exist")
