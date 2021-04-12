import pandas
import grammar_check
import keywords
import feedback
import format
from pdfminer.high_level import extract_text


class Grade:
    # Technically the last field can be voided if you are either not grading format or only using the raw text function
    def __init__(self, rubric_list, weight_list, dictionary_path='./data/dictionary.tsv', expected_format=None):
        self.rubric = rubric_list
        self.weights = weight_list
        self.expected_format = expected_format

        try:
            self.words = keywords.KeyWords(dictionary_path)
        except FileNotFoundError:
            print("Can't find file given path")

    # Given raw text, print the grade with feedback
    def get_grade_raw(self, text):
        grade, key_total, grammar_points, key_points, length_score = 100, 0, 0, 0, 1
        key_list = []
        debug, output = "", ""

        # Remove the necessary points from the score
        if self.rubric['grammar'] is not None:
            grade -= self.rubric['grammar']
        if self.rubric['key'] is not None:
            grade -= self.rubric['key']
        if self.rubric['length'] is not None:
            grade -= self.rubric['length']

        # Correct the text first for a more accurate word count and key word examination
        corrections, corrected_text = grammar_check.number_of_errors(text)
        word_count = len(corrected_text.split())

        # Calculate how many points from grammar is earned
        if self.rubric['grammar'] is not None:
            grammar_points = max(self.rubric['grammar'] - self.weights['grammar'] * len(corrections), 0)
            grade += grammar_points

        # Calculate how many points are earned from including keywords
        if self.rubric['key'] is not None:
            key_list = self.words.occurrence(corrected_text)
            for i in key_list:
                if i[1] > 0:
                    key_total += 1
            key_points = max(self.rubric['key'] - self.weights['key'] * (self.weights['key_min'] - key_total), 0)
            grade += key_points

        # If the essay is within word bounds, earn 100% points, under the bounds is 0%, and over the bounds is 50%
        if self.rubric['length'] is not None:
            if self.weights['word_min'] is not None:
                if word_count < self.weights['word_min']:
                    length_score = 0
            if self.weights['word_max'] is not None:
                if word_count > self.weights['word_max']:
                    length_score = 2
                    grade += round(self.rubric['length'] / 2)
            if length_score == 1:
                grade += self.rubric['length']

        # Depending on the rubric, it may be possible to get a negative score
        if grade < 0:
            grade = 0

        # Begin putting together the output text
        if self.rubric['grammar'] is not None:
            debug += "Errors: " + str(len(corrections)) + "\n"
            debug += str(corrections) + "\n"
        if self.rubric['key'] is not None:
            debug += "Keyword Usage: " + str(key_list) + "\n"
        if self.rubric['length'] is not None:
            debug += "Word Count: " + str(word_count) + "\n"

        if self.rubric['grammar'] is not None:
            output += feedback.grammar_feedback(grammar_points, self.rubric['grammar'])
        if self.rubric['key'] is not None:
            output += feedback.keyword_feedback(key_points, self.rubric['key'])
        if self.rubric['length'] is not None:
            output += feedback.length_feedback(length_score)

        return debug, grade, output

    # Given a file path to a docx, print the grade with feedback
    def get_grade_docx(self, file_path):
        grade, key_total, grammar_points, key_points, length_score = 100, 0, 0, 0, 1
        key_list, format_bool = [], [False] * 16
        debug, output = "", ""

        try:
            word_doc = format.Format(file_path)
            word_count = word_doc.get_word_count()
            page_count = word_doc.get_page_count()
            default_style = word_doc.get_default_style()
        except FileNotFoundError:
            return None, None, None


        # Remove the necessary points from the score
        if self.rubric['grammar'] is not None:
            grade -= self.rubric['grammar']
        if self.rubric['key'] is not None:
            grade -= self.rubric['key']
        if self.rubric['length'] is not None:
            grade -= self.rubric['length']
        if self.rubric['format'] is not None:
            grade -= self.rubric['format']

        # Correct the text first for a more accurate word count and key word examination
        corrections, corrected_text = grammar_check.number_of_errors(word_doc.get_text())

        # Calculate how many points from grammar is earned
        if self.rubric['grammar'] is not None:
            grammar_points = max(self.rubric['grammar'] - self.weights['grammar'] * len(corrections), 0)
            grade += grammar_points

        # Calculate how many points are earned from including keywords
        if self.rubric['key'] is not None:
            key_list = self.words.occurrence(corrected_text)
            for i in key_list:
                if i[1] > 0:
                    key_total += 1
            key_points = max(self.rubric['key'] - self.weights['key'] * (self.weights['key_min'] - key_total), 0)
            grade += key_points

        # If the essay is within word bounds, earn 100% points, under the bounds is 0%, and over the bounds is 50%
        if self.rubric['length'] is not None:
            if self.weights['page_min'] is not None:
                if page_count < self.weights['page_min']:
                    length_score = 0
            if self.weights['page_max'] is not None:
                if page_count > self.weights['page_max']:
                    length_score = 2
            if self.weights['word_min'] is not None:
                if word_count < self.weights['word_min']:
                    length_score = 0
            if self.weights['word_max'] is not None:
                if word_count > self.weights['word_max']:
                    length_score = 2

            if length_score == 1:
                grade += self.rubric['length']
            if length_score == 2:
                grade += self.rubric['length'] / 2

        # For every format mistake, take off points. All errors are equal here
        if self.rubric['format'] is not None:
            best_case = self.rubric['format']

            fonts = word_doc.get_font()
            spacing = word_doc.get_spacing()
            indent = word_doc.get_indentation()
            margin = word_doc.get_margin()

            if self.expected_format['font'] is not None:
                for f in fonts:
                    if f[0] not in self.expected_format['font']:
                        best_case -= self.weights['format']
                        format_bool[0] = True
            if self.expected_format['size'] is not None:
                for f in fonts:
                    if f[1] != self.expected_format['size']:
                        best_case -= self.weights['format']
                        format_bool[1] = True
            if self.expected_format['line_spacing'] is not None:
                for s in spacing:
                    if s[0] != self.expected_format['line_spacing']:
                        best_case -= self.weights['format']
                        format_bool[2] = True
            if self.expected_format['after_spacing'] is not None:
                for s in spacing:
                    if s[1] != self.expected_format['after_spacing']:
                        best_case -= self.weights['format']
                        format_bool[3] = True
            if self.expected_format['before_spacing'] is not None:
                for s in spacing:
                    if s[2] != self.expected_format['before_spacing']:
                        best_case -= self.weights['format']
                        format_bool[4] = True
            if self.expected_format['page_width'] is not None:
                if default_style['page_width'] != self.expected_format['page_width']:
                    best_case -= self.weights['format']
                    format_bool[5] = True
            if self.expected_format['page_height'] is not None:
                if default_style['page_height'] != self.expected_format['page_height']:
                    best_case -= self.weights['format']
                    format_bool[6] = True
            if self.expected_format['left_margin'] is not None:
                if default_style['left_margin'] != self.expected_format['left_margin']:
                    best_case -= self.weights['format']
                    format_bool[7] = True
            if self.expected_format['bottom_margin'] is not None:
                if default_style['bottom_margin'] != self.expected_format['bottom_margin']:
                    best_case -= self.weights['format']
                    format_bool[8] = True
            if self.expected_format['right_margin'] is not None:
                if default_style['right_margin'] != self.expected_format['right_margin']:
                    best_case -= self.weights['format']
                    format_bool[9] = True
            if self.expected_format['top_margin'] is not None:
                if default_style['top_margin'] != self.expected_format['top_margin']:
                    best_case -= self.weights['format']
                    format_bool[10] = True
            if self.expected_format['header'] is not None:
                if default_style['header'] != self.expected_format['header']:
                    best_case -= self.weights['format']
                    format_bool[11] = True
            if self.expected_format['footer'] is not None:
                if default_style['footer'] != self.expected_format['footer']:
                    best_case -= self.weights['format']
                    format_bool[12] = True
            if self.expected_format['gutter'] is not None:
                if default_style['gutter'] != self.expected_format['gutter']:
                    best_case -= self.weights['format']
                    format_bool[13] = True
            if self.expected_format['indent'] is not None:
                if self.expected_format['indent'] < 0.5:
                    best_case -= min(self.weights['format'] * (indent - self.expected_format['indent']) * 2,
                                     self.weights['format'])
                else:
                    best_case -= max(min(self.weights['format'] * (self.expected_format['indent'] - indent) * 2,
                                         self.weights['format']), 0)
                if self.expected_format['indent'] != indent:
                    format_bool[14] = True
            if self.expected_format['left_margin'] is not None and self.expected_format['right_margin'] is not None:
                best_case -= min(self.weights['format'] * margin, self.weights['format'])
                if margin != 0:
                    format_bool[15] = True

            grade = grade + round(best_case)

        # Depending on the rubric, it may be possible to get a negative score
        if grade < 0:
            grade = 0

        # Begin putting together the output text
        if self.rubric['grammar'] is not None:
            debug += "Errors: " + str(len(corrections)) + "\n" + str(corrections) + "\n"
        if self.rubric['key'] is not None:
            debug += "Keyword Usage: " + str(key_list) + "\n"
        if self.rubric['length'] is not None:
            debug += "Word Count: " + str(word_count) + "\n"
        if self.rubric['format'] is not None:
            debug += "Default Style: " + str(default_style) + "\nFonts: " + str(word_doc.get_font_table()) + "\n"

        if self.rubric['grammar'] is not None:
            output += feedback.grammar_feedback(grammar_points, self.rubric['grammar'])
        if self.rubric['key'] is not None:
            output += feedback.keyword_feedback(key_points, self.rubric['key'])
        if self.rubric['length'] is not None:
            output += feedback.length_feedback(length_score)
        if self.rubric['format'] is not None:
            output += feedback.format_feedback(format_bool)

        return debug, grade, output

    # Honestly, due to PDF's lack of readable format storage, format grading is off limits for PDF's for now
    def get_grade_pdf(self, file_path):
        try:
            text = extract_text(file_path)
            # PDF reader has trouble dealing with large line spacing, so this is an attempt to fix it.
            text = text.replace("\n\n", " ").replace("  ", " ").replace("  ", " ")

            return self.get_grade_raw(text)

        except FileNotFoundError:
            return None, None, None
