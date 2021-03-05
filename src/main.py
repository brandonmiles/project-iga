from score_model import ScoreModel
import pandas as pd
import grade

#	g = grade.Grade('../data/dictionary.tsv', 1, 1, 5)

try:
    #test_data = pd.read_csv('../data/test_set.tsv', sep='\t', encoding='ISO-8859-1')
    # Table column names are "essay_id", "essay_set", "essay", "domain1_predictionid", "domain2_predictionid"

    # Uncomment if you want to run the model.
    model = ScoreModel()
    #model.train_and_test('../data/training_set.tsv')
    model.test_evaluate()

    # Grammar Check
    #for i in test_data['essay']:
        #g.get_grade(i)

except FileNotFoundError:
    print("File does not exist")
