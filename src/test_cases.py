import format
import grammar_check
import os
import unittest
from json import JSONDecodeError
from keywords import KeyWords
from zipfile import BadZipFile
# from score_model import Model, ScoreModel, IdeaModel, OrganizationModel, StyleModel
# from grade import Grade

FILEPATH = '../data/test_cases/'


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


class FormatUnit(unittest.TestCase):
    def test_format_not_found(self):
        with self.assertRaises(FileNotFoundError):
            format.get_format_file('BAD_PATH.NONEXISTENT')

    def test_bad_format_file(self):
        with self.assertRaises(JSONDecodeError):
            format.get_format_file(FILEPATH + 'bad_format.txt')

    def test_format_missing_key(self):
        with self.assertRaises(KeyError):
            format.get_format_file(FILEPATH + 'missing_key.json')

    def test_format_key_error(self):
        with self.assertRaises(KeyError):
            format.update_format_file('./temp.json', {'hello': 'world'})
            os.remove('./temp.json')

    def test_correct_storage(self):
        format.update_format_file('./temp.json', format.get_style())
        self.assertEqual(format.get_format_file('./temp.json'),
                         format.get_style(), "format improperly stored the json file.")
        os.remove('./temp.json')

    def test_file_not_found(self):
        with self.assertRaises(FileNotFoundError):
            format.Format('BAD_PATH.NONEXISTENT')

    def test_bad_file(self):
        with self.assertRaises(BadZipFile):
            format.Format(FILEPATH + 'bad_format.txt')

    def test_broken_word_docx(self):
        with self.assertRaises(KeyError):
            format.Format(FILEPATH + 'broken.docx')

    def test_empty_docx(self):
        f = format.Format(FILEPATH + 'empty.docx')
        self.assertEqual(f.get_text(), '', "Couldn't recognize an empty file contains no text.")
        self.assertEqual(f.get_word_count(), 0, "Couldn't recognize an empty file contains no words.")
        self.assertEqual(f.get_page_count(), 1, "Couldn't recognize an empty file contains one pages.")
        self.assertEqual(f.get_font(), [], "Couldn't recognize an empty file contains no used fonts.")

    def test_single_font_recognition(self):
        f = format.Format(FILEPATH + 'single_font.docx')
        self.assertEqual(f.get_font(), [("Times New Roman", 12)], "format gave an incorrect font list.")

    def test_multi_font_recognition(self):
        f = format.Format(FILEPATH + 'multiple_font.docx')
        self.assertEqual(f.get_font(),
                         [("Times New Roman", 12), ("Times New Roman", 16), ('Aharoni', 12.0), ('Akbar', 12.0),
                         ('Arial Black', 12.0), ('Arial Black', 10.0), ('Times New Roman', 10.0), ('Arial', 12.0)],
                         "format gave an incorrect font list.")

    def test_spacing_recognition(self):
        f = format.Format(FILEPATH + 'single_spacing.docx')
        self.assertEqual(f.get_spacing(), [(1.0, 0.0, 0.0)], "format returned incorrect spacing list")

    def test_multiple_spacing_recognition(self):
        f = format.Format(FILEPATH + 'multiple_spacing.docx')
        self.assertEqual(f.get_spacing(),
                         [(1.0, 0.0, 0.0), (1.15, 8.0, 12.0), (3.0, 0.0, 12.0)],
                         "format returned incorrect spacing list")

    def test_no_indent(self):
        f = format.Format(FILEPATH + 'no_indent.docx')
        self.assertEqual(f.get_indentation(), 0.0, "format couldn't correctly calculate indention score")

    def test_all_indent(self):
        f = format.Format(FILEPATH + 'all_indent.docx')
        self.assertEqual(f.get_indentation(), 1.0, "format couldn't correctly calculate indention score")

    def test_mixed_indent(self):
        f = format.Format(FILEPATH + 'mixed_indent.docx')
        self.assertEqual(f.get_indentation(), 0.5, "format couldn't correctly calculate indention score")

    def test_consistent_margin(self):
        f = format.Format(FILEPATH + 'consistent_margin.docx')
        self.assertEqual(f.get_margin(), 0.0, "format couldn't correctly calculate margin score")

    def test_mixed_margin(self):
        f = format.Format(FILEPATH + 'mixed_margin.docx')
        self.assertEqual(f.get_margin(), 1.25, "format couldn't correctly calculate margin score")


if __name__ == "__main__":
    unittest.main()
