# from score_model import ScoreModel
import pandas as pd
import grade
import format


# How many points each graded section is worth
rubric = {'Grammar': 20, 'Key': 20}
# How easily or hard it is to lose points from each sections
weights = {'Grammar': 1, 'Key': 10, 'Key_Min': 2}
g = grade.Grade('../data/dictionary.tsv', rubric, weights)

try:
    test_data = pd.read_csv('../data/test_set.tsv', sep='\t', encoding='ISO-8859-1')
    # Table column names are "essay_id", "essay_set", "essay", "domain1_predictionid", "domain2_predictionid"

    # Currently testing the ability to get information from a word document
    word_doc = format.Format('../data/ay.docx')
    print("Fonts Table: ", word_doc.get_font_table())
    print("Words: ", word_doc.get_word_count())
    print("Pages: ", word_doc.get_page_count())
    print("Default Style: ", word_doc.get_default_style())
    print("Fonts: ", word_doc.get_font())

    # Uncomment if you want to run the model.
    # model = ScoreModel()
    # model.train_and_test('../data/training_set.tsv')

    # Grade each essay
    a = 0
    for i in test_data['essay']:
        a = a + 1
        print("Essay: ", a)
        g.get_grade(i)

except FileNotFoundError:
    print("File does not exist")
