# from score_model import ScoreModel
import pandas as pd
import grade


# How many points each graded section is worth, use None to remove from the rubric
rubric = {'grammar': 20, 'key': 20, 'length': 20, 'format': 20}
# How easily or hard it is to lose points from each sections, use None to chose between word count and page count
weights = {'grammar': 1, 'key': 10, 'key_min': 2, 'word_min': 300, 'word_max': None, 'page_min': None, 'page_max': None,
           'format': 5}
# List of allowable fonts
allowed_fonts = ["Times New Roman", "Calibri Math"]
# Expected format of the word document, use None to denote a non-graded format criteria
expected_style = {'font': allowed_fonts, 'size': 12, 'line_spacing': 2.0, 'after_spacing': 0.0,
                  'before_spacing': 0.0, 'page_width': 8.5, 'page_height': 11, 'left_margin': 1.0, 'bottom_margin': 1.0,
                  'right_margin': 1.0, 'top_margin': 1.0, 'header': None, 'footer': None, 'gutter': 0.0, 'indent': 1.0}
g = grade.Grade(rubric, weights, expected_format=expected_style)

try:
    test_data = pd.read_csv('../data/test_set.tsv', sep='\t', encoding='ISO-8859-1')
    # Table column names are "essay_id", "essay_set", "essay", "domain1_predictionid", "domain2_predictionid"

    # Currently testing the ability to get information from a word document
    db, gd, out = g.get_grade_docx('../data/ay.docx')
    print(db)
    print(gd)
    print(out)

    # Uncomment if you want to run the model.
    # model = ScoreModel()
    # model.train_and_test('../data/training_set.tsv')

    # Grade each essay
    a = 0
    for i in test_data['essay']:
        a += 1
        print("---------------------------------------------------------------------------------------------------\n")
        print("Essay: ", a)
        db, gd, out = g.get_grade_raw(i)
        print(db)
        print(gd)
        print(out)

except FileNotFoundError:
    print("File does not exist")
