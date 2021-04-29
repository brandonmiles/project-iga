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

    def test_init_type_error(self):
        with self.assertRaises(TypeError):
            self.word = KeyWords(69)

    def test_add_type_error(self):
        with self.assertRaises(TypeError):
            self.word.add_keyword(69)

    def test_remove_type_error(self):
        with self.assertRaises(TypeError):
            self.word.remove_keyword(69)

    def test_occurrence_type_error(self):
        with self.assertRaises(TypeError):
            self.word.occurrence(69)

    def test_good_path(self):
        self.word = KeyWords('./temp.csv')
        self.assertEqual(self.word.get_keywords(), [], "KeyWords couldn't access the newly made file correctly.")

    def test_single_word(self):
        self.file.write("hello")
        self.file.close()
        self.word = KeyWords('./temp.csv')
        self.assertEqual(self.word.get_keywords(), ['hello'], "KeyWords couldn't get keywords from the file correctly.")

    def test_multiple_words(self):
        self.file.write("hello,world")
        self.file.close()
        self.word = KeyWords('./temp.csv')
        self.assertEqual(self.word.get_keywords(), ['hello', 'world'], "KeyWords couldn't get keywords from the file "
                                                                       "correctly.")

    def test_added_keyword(self):
        self.word.add_keyword('hello')
        self.assertEqual(self.word.get_keywords(), ['hello'], "KeyWords couldn't add keywords correctly")

    def test_add_keyword_via_file(self):
        self.word = KeyWords('./temp.csv')
        self.word.add_keyword('hello')
        word2 = KeyWords('./temp.csv')
        self.assertEqual(word2.get_keywords(), ['hello'], "KeyWords couldn't add keywords correctly to a file")

    def test_removed_keyword(self):
        self.word.add_keyword('hello')
        self.word.remove_keyword('Hello')
        self.assertEqual(self.word.get_keywords(), [], "KeyWords couldn't remove a keyword correctly")

    def test_remove_keyword_via_file(self):
        self.word = KeyWords('./temp.csv')
        self.word.add_keyword('hello')
        self.word.remove_keyword('Hello')
        word2 = KeyWords('./temp.csv')
        self.assertEqual(word2.get_keywords(), [], "KeyWords couldn't remove keywords from a file")

    def test_single_occurrence(self):
        self.word.add_keyword('hello')
        self.assertEqual(
            self.word.occurrence("Hello None of this hello text makes yhello much hElLo"),
            [('hello', 3)], "Couldn't count all instances of a keyword")

    def test_multi_occurrence(self):
        self.word.add_keyword('hello')
        self.word.add_keyword('world')
        self.assertEqual(
            self.word.occurrence("Hello None world this helloworld text WoRld yhello much hElLo"),
            [('hello', 2), ('world', 2)], "Couldn't count all instances of multiple keyword")

    def test_empty_occurrenceA(self):
        self.word.add_keyword('hello')
        self.assertEqual(
            self.word.occurrence(""), [('hello', 0)], "Couldn't handle empty text")

    def test_empty_occurrenceB(self):
        self.assertEqual(
            self.word.occurrence("This is a fun test text"), [], "Couldn't handle empty KeyWords")


if __name__ == "__main__":
    unittest.main()
