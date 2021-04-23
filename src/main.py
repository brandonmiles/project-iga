import os
import pandas
from grade import Grade


# How many points each graded section is worth, use None to remove from the rubric
rubric = {'grammar': 20, 'key': 10, 'length': 20, 'format': 20, 'model': 20, 'reference': 10}
# How easily or hard it is to lose points from each sections, use None to chose between word count and page count
weights = {'grammar': 1, 'allowed_mistakes': 3, 'key_max': 2, 'key_min': 0, 'word_min': 300, 'word_max': None,
           'page_min': None, 'page_max': None, 'format': 5, 'reference': 5}

def main():
    g = Grade(rubric, weights)

    try:
        test_data = pandas.read_csv(os.relpath('../data/test_set.tsv', start='src'), sep='\t', encoding='ISO-8859-1')

        # Grade each essay
        a = 0
        for i in test_data['essay']:
            a += 1
            print("-----------------------------------------------------------------------------------------------------\n")
            print("Essay: ", a)
            db, gd, out = g.get_grade(i)
            print(db + "Grade: " + str(gd) + "\n" + out)

    except FileNotFoundError:
        print("../data/test_set.tsv not found")

# This stops all the code from running when Sphinx imports the module.
if __name__ == '__main__':
    main()