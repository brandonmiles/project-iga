import pandas as pd
from grade import Grade
import nltk


# How many points each graded section is worth, use None to remove from the rubric
rubric = {'grammar': 20, 'key': 10, 'length': 20, 'format': 20, 'model': 20, 'reference': 10}
# How easily or hard it is to lose points from each sections, use None to chose between word count and page count
weights = {'grammar': 1, 'key': 5, 'key_min': 2, 'word_min': 300, 'word_max': None, 'page_min': None, 'page_max': None,
           'format': 5, 'reference': 5}
g = Grade(rubric, weights)

try:
    test_data = pd.read_csv('../data/test_set.tsv', sep='\t', encoding='ISO-8859-1')

    # g.retrain_score('../data/training_set.tsv')

    g.retrain_feedback('../data/comment_set.csv')

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
