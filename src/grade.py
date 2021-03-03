import pandas
import grammar_check
import keywords


class Grade:
    words = keywords.KeyWords
    weights = {}

    def __init__(self, dictionary_path, grammar_weight, key_weight, key_min):
        self.weights = {'Grammar': grammar_weight, 'Key': key_weight, 'Key_Min': key_min}

        try:
            self.words = keywords.KeyWords(dictionary_path)
        except FileNotFoundError:
            print("Can't find file given path")

    # Given a list of tokens, return a tuple of the number of errors and the misspelled words in question
    def get_grade(self, text):
        grade = 100
        key_total = 0

        corrections, corrected_text = grammar_check.number_of_errors(text)
        key_list = self.words.occurrence(corrected_text)
        for i in key_list:
            key_total = key_total + i[1]
        grade = grade - self.weights["Grammar"] * len(corrections) - self.weights["Key"] * max(self.weights["Key_Min"] -
                                                                                               key_total, 0)
        if grade < 0:
            grade = 0

        print("Essay: ", i, "Errors: ", len(corrections))
        print(corrections)
        print(key_list)
        print("Grade: ", grade)
