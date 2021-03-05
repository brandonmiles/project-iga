import pandas
import grammar_check
import keywords
import feedback


class Grade:
    def __init__(self, dictionary_path, rubric_list, weight_list):
        self.rubric = rubric_list
        self.weights = weight_list

        try:
            self.words = keywords.KeyWords(dictionary_path)
        except FileNotFoundError:
            print("Can't find file given path")

    # Given a list of tokens, return a tuple of the number of errors and the misspelled words in question
    def get_grade(self, text):
        grade = 100 - self.rubric["Grammar"] - self.rubric["Key"]
        key_total = 0

        corrections, corrected_text = grammar_check.number_of_errors(text)

        # Whenever an item from the keyword list is included, add a point
        key_list = self.words.occurrence(corrected_text)
        for i in key_list:
            if i[1] > 0:
                key_total = key_total + 1

        # Calculate how many points from each section they get to keep
        grammar_points = max(self.rubric["Grammar"] - self.weights["Grammar"] * len(corrections), 0)
        key_points = max(self.rubric["Key"] - self.weights["Key"] * (self.weights["Key_Min"] - key_total), 0)

        # Return earned points
        grade = grade + grammar_points + key_points

        if grade < 0:
            grade = 0

        # Begin printing
        print("Errors: ", len(corrections))
        print(corrections)
        print("Keyword usage: ", key_list)
        print("Grade: ", grade)
        print(feedback.grammar_feedback(grammar_points, self.rubric["Grammar"]))
        print(feedback.keyword_feedback(key_points, self.rubric["Key"]))
