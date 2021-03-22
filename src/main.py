# from score_model import ScoreModel
import pandas as pd
from grade import Grade


# How many points each graded section is worth, use None to remove from the rubric
rubric = {'grammar': 20, 'key': 20, 'length': 20, 'format': 20}
# How easily or hard it is to lose points from each sections, use None to chose between word count and page count
weights = {'grammar': 1, 'key': 10, 'key_min': 2, 'word_min': 300, 'word_max': None, 'page_min': None, 'page_max': None,
           'format': 5}
g = Grade(rubric, weights)

try:
    test_data = pd.read_csv('../data/test_set.tsv', sep='\t', encoding='ISO-8859-1')
    # Table column names are "essay_id", "essay_set", "essay", "domain1_predictionid", "domain2_predictionid"

    # Uncomment if you want to run the model.
    # model = ScoreModel()
    # Change the int to which essay set you want to grade the model against.
    # model.train_and_test('../data/training_set.tsv', 1)
    # model.test_evaluate()

    # Grade each essay
    a = 0
    for i in test_data['essay']:
        a += 1
        print("-----------------------------------------------------------------------------------------------------\n")
        print("Essay: ", a)
        db, gd, out = g.get_grade_raw(i)
        print(db, "Grade:", gd, "\n", out)

except FileNotFoundError:
    print("File does not exist")
