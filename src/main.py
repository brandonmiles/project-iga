from score_model import ScoreModel
import pandas as pd
import grade

<<<<<<< HEAD
#	g = grade.Grade('../data/dictionary.tsv', 1, 1, 5)
=======
# How many points each graded section is worth
rubric = {'Grammar': 20, 'Key': 20}
# How easily or hard it is to lose points from each sections
weights = {'Grammar': 1, 'Key': 10, 'Key_Min': 2}
g = grade.Grade('../data/dictionary.tsv', rubric, weights)
>>>>>>> 347d22261265d01a7071a3c457f3b5540a7ea53b

try:
    #test_data = pd.read_csv('../data/test_set.tsv', sep='\t', encoding='ISO-8859-1')
    # Table column names are "essay_id", "essay_set", "essay", "domain1_predictionid", "domain2_predictionid"

    # Uncomment if you want to run the model.
    model = ScoreModel()
<<<<<<< HEAD
    #model.train_and_test('../data/training_set.tsv')
    model.test_evaluate()

    # Grammar Check
    #for i in test_data['essay']:
        #g.get_grade(i)
=======
    model.train_and_test('../data/training_set.tsv')

    # Grade each essay
    a = 0
    for i in test_data['essay']:
        a = a + 1
        print("Essay: ", a)
        g.get_grade(i)
>>>>>>> 347d22261265d01a7071a3c457f3b5540a7ea53b

except FileNotFoundError:
    print("File does not exist")
