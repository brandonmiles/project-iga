# from score_model import ScoreModel
import pandas as pd
import grammar_check
import keywords


words = keywords.KeyWords('../data/dictionary.tsv')

try:
    test_data = pd.read_csv('../data/test_set.tsv', sep='\t', encoding='ISO-8859-1')
    # Table column names are "essay_id", "essay_set", "essay", "domain1_predictionid", "domain2_predictionid"

    # Uncomment if you want to run the model.
    # model = ScoreModel()
    # model.train_and_test('../data/training_set.tsv')

    # Grammar Check
    for i in range(len(test_data['essay'])):
        corrections, corrected_text = grammar_check.number_of_errors(test_data['essay'][i])
        print("Essay: ", i, "Errors: ", len(corrections))
        print(corrections)
        print(words.occurrence(corrected_text))

except FileNotFoundError:
    print("File does not exist")
