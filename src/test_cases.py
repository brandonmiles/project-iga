# import pandas
import unittest
import grammar_check
import os
from keywords import KeyWords
# from format import Format
# from score_model import Model, ScoreModel, IdeaModel, OrganizationModel, StyleModel
# from grade import Grade


class GrammarUnit(unittest.TestCase):
    def test_pass_not_str(self):
        with self.assertRaises(TypeError):
            grammar_check.number_of_errors(["A", "quick", "brown", "fox", "jumped", "over", "the", "lazy", "dog"])

    def test_empty_str(self):
        self.assertEqual(grammar_check.number_of_errors(""), ([], ""), "grammar_check.py can't handle empty strings")

    def test_normal(self):
        self.assertEqual(grammar_check.number_of_errors("They help you stay in touch with family in a couple \
different ways they excercise your mind and hands and help you learn and make things easier."),
                         ([('excercise', 'exercise')], "They help you stay in touch with family in a couple different \
ways they exercise your mind and hands and help you learn and make things easier."),
                         "grammar_checck.py doesn't return expected answer.")

    def test_correct_word(self):
        self.assertEqual(grammar_check.number_of_errors("exercise"), ([], "exercise"),
                         "grammar_check.py give incorrect return for a single correct word.")

    def test_incorrect_word(self):
        self.assertEqual(grammar_check.number_of_errors("exrcise"), ([("exrcise", "exercise")], "exercise"),
                         "grammar_check.py give incorrect return for a single correct word.")


class KeyWordUnit(unittest.TestCase):
    def setUp(self):
        self.word = KeyWords()
        self.file = open('temp.csv', 'w')

    def tearDown(self):
        self.word = None
        self.file.close()
        os.remove('temp.csv')

    def test_blank_init(self):
        self.assertEqual(self.word.get_keywords(), [], "KeyWords doesn't initialize empty correctly.")

    def test_bad_path(self):
        with self.assertRaises(FileNotFoundError):
            self.word = KeyWords('./BAD_PATH.NONEXISTENT')

    def test_good_path(self):
        self.word = KeyWords('./temp.csv')
        self.assertEqual(self.word.get_keywords(), [''], "KeyWords couldn't access the newly made file correctly.")


if __name__ == "__main__":
    unittest.main()
