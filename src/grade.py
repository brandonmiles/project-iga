import grammar_check
import keywords
import feedback
import format
import references
from score_model import ScoreModel
from pdfminer.high_level import extract_text

STYLE_SKELETON = {'font': None, 'size': None, 'line_spacing': None, 'after_spacing': None, 'before_spacing': None,
                  'page_width': None, 'page_height': None, 'left_margin': None, 'bottom_margin': None,
                  'right_margin': None, 'top_margin': None, 'header': None, 'footer': None, 'gutter': None}

RUBRIC_SKELETON = {'grammar': None, 'key': None, 'length': None, 'format': None, 'model': None, 'reference': None}

WEIGHTS_SKELETON = {'grammar': None, 'allowed_mistakes': None, 'key_max': None, 'key_min': None, 'word_min': None,
                    'word_max': None, 'page_min': None, 'page_max': None, 'format': None, 'reference': None}


class Grade:
    # Technically the last field can be voided if you are either not grading format or only using the raw text function
    def __init__(self, rubric, weights, dictionary_path='../data/dictionary.csv', style=None,
                 style_path='../data/standard.json'):
        self.rubric = rubric
        self.weights = weights
        self.model = ScoreModel()
        self.idea_model = ScoreModel(name="idea")
        self.organization_model = ScoreModel(name="organization")
        self.style_model = ScoreModel(name="style")

        if set(rubric.keys()) == set(RUBRIC_SKELETON.keys()):
            self.rubric = rubric
        else:
            raise Exception("Given rubric keys do not match skeleton keys")
        if set(weights) == set(WEIGHTS_SKELETON.keys()):
            self.weights = weights
        else:
            raise Exception("Given weight keys do not match skeleton keys")
        if style is not None:
            if set(style.keys() == set(STYLE_SKELETON.keys())):
                self.style = style
            else:
                raise Exception("Given style keys do not match skeleton keys")
        else:
            if style_path is not None:
                self.style = format.get_format_file(style_path)

        if dictionary_path is not None:
            try:
                self.words = keywords.KeyWords(dictionary_path)
            except FileNotFoundError:
                print(str(dictionary_path) + " not found")

    # Specify whether you are giving raw text or a file path, will return the debug, grade, and output in that order
    def get_grade(self, text=None, filepath=None):
        grade, page, word = 100, None, None
        debug, output, t = "", "", ""

        if (text is None and filepath is None) or (text is not None and filepath is not None):
            return None, None, None

        if text is not None:
            t = text
        else:
            f = filepath.split('.')

            if f[len(f) - 1] == "docx" or f[len(f) - 1] == "doc":
                try:
                    word = format.Format(filepath)
                    t = word.get_text()
                    page = word.get_page_count()
                except FileNotFoundError:
                    return None, None, None
            if f[len(f) - 1] == "pdf":
                try:
                    t = extract_text(filepath)
                    # PDF reader has trouble dealing with large line spacing, so this is an attempt to fix it.
                    t = t.replace("\n\n", " ").replace("  ", " ").replace("  ", " ")
                except FileNotFoundError:
                    return None, None, None

        p, corrected_text, d, o = self.grade_grammar(t)
        grade -= p
        debug += d
        output += o

        p, d, o = self.grade_key(corrected_text)
        grade -= p
        debug += d
        output += o

        p, d, o = self.grade_length(corrected_text, page)
        grade -= p
        debug += d
        output += o

        p, d, o = self.grade_format(word)
        grade -= p
        debug += d
        output += o

        p, d, o = self.grade_model(corrected_text)
        grade -= p
        debug += d
        output += o

        p, d, o = self.grade_reference(corrected_text)
        grade -= p
        debug += d
        output += o

        return debug, max(grade, 0), output

    # This function will return the points lost, corrected text, debug text, and feedback text in that order
    def grade_grammar(self, text):
        points = 0
        debug, output = "", ""

        corrections, corrected_text = grammar_check.number_of_errors(text)
        if self.rubric['grammar'] is not None:
            mistakes = len(corrections)
            if self.weights['allowed_mistakes'] is not None:
                mistakes = max(mistakes - self.weights['allowed_mistakes'], 0)

            points = min(self.weights['grammar'] * mistakes, self.rubric['grammar'])
            debug += "Errors: " + str(len(corrections)) + "\n"
            debug += str(corrections) + "\n"
            output += feedback.grammar_feedback(round(points * 3 / self.rubric['grammar']))

        return points, corrected_text, debug, output

    # This function will return the points lost, debug text, and feedback text in that order
    def grade_key(self, text):
        points, key = 0, 0
        debug, output = "", ""

        if self.rubric['key'] is not None:
            key_list = self.words.occurrence(text)
            for i in key_list:
                if i[1] > 0:
                    key += 1
            points = max((self.weights['key_max'] - key) / (self.weights['key_max'] - self.weights['key_min']), 0.0)
            points = min(round(points * self.rubric['key']), self.rubric['key'])
            debug += "Keyword Usage: " + str(key_list) + "\n"
            output += feedback.keyword_feedback(round(points * 3 / self.rubric['key']))

        return points, debug, output

    # This function will return the points lost, debug text, and feedback text in that order
    def grade_length(self, text, page=None):
        points = 0
        debug, output = "", ""

        count = len(text.split())
        if self.rubric['length'] is not None:
            if self.weights['page_min'] is not None and page is not None and page < self.weights['page_min']:
                points = self.rubric['length']
            if self.weights['page_max'] is not None and page is not None and page > self.weights['page_max']:
                points = round(self.rubric['length'] / 2)
            if self.weights['word_min'] is not None and page is None and count < self.weights['word_min']:
                points = self.rubric['length']
            if self.weights['word_max'] is not None and page is None and count > self.weights['word_max']:
                points = round(self.rubric['length'] / 2)

            if page is not None:
                debug += "Page Count: " + str(page) + "\n"
            debug += "Word Count: " + str(count) + "\n"
            output += feedback.length_feedback(round(points * 2 / self.rubric['length']))

        return points, debug, output

    # This function will return the points lost, debug text, and feedback text in that order
    def grade_model(self, text):
        points = 0
        debug, output = "", ""

        if self.rubric['model'] is not None:
            points = self.model.evaluate(text)
            idea_score = round(self.idea_model.evaluate(text) * 2)
            organization_score = round(self.organization_model.evaluate(text) * 2)
            style_score = round(self.style_model.evaluate(text) * 2)

            debug += "Model Score: " + str(points) + "\n"
            points = round(self.rubric['model'] * (1 - points))
            debug += "Idea Score: " + str(idea_score) + "\n"
            debug += "Organization Score: " + str(organization_score) + "\n"
            debug += "Style Score: " + str(style_score) + "\n"
            output += feedback.idea_feedback(idea_score)
            output += feedback.organization_feedback(organization_score)
            output += feedback.style_feedback(style_score)

        return points, debug, output

    # This function will return the points lost, debug text, and feedback text in that order
    def grade_format(self, word):
        points = 0
        debug, output = "", ""
        format_bool = [False] * 16

        if self.rubric['format'] is not None and word is not None:
            fonts = word.get_font()
            spacing = word.get_spacing()
            indent = word.get_indentation()
            margin = word.get_margin()
            default_style = word.get_default_style()

            if self.style['font'] is not None:
                for f in fonts:
                    if f[0] not in self.style['font']:
                        points += self.weights['format']
                        format_bool[0] = True
            if self.style['size'] is not None:
                for f in fonts:
                    if f[1] != self.style['size']:
                        points += self.weights['format']
                        format_bool[1] = True
            if self.style['line_spacing'] is not None:
                for s in spacing:
                    if s[0] != self.style['line_spacing']:
                        points += self.weights['format']
                        format_bool[2] = True
            if self.style['after_spacing'] is not None:
                for s in spacing:
                    if s[1] != self.style['after_spacing']:
                        points += self.weights['format']
                        format_bool[3] = True
            if self.style['before_spacing'] is not None:
                for s in spacing:
                    if s[2] != self.style['before_spacing']:
                        points += self.weights['format']
                        format_bool[4] = True
            if self.style['page_width'] is not None:
                if default_style['page_width'] != self.style['page_width']:
                    points += self.weights['format']
                    format_bool[5] = True
            if self.style['page_height'] is not None:
                if default_style['page_height'] != self.style['page_height']:
                    points += self.weights['format']
                    format_bool[6] = True
            if self.style['left_margin'] is not None:
                if default_style['left_margin'] != self.style['left_margin']:
                    points += self.weights['format']
                    format_bool[7] = True
            if self.style['bottom_margin'] is not None:
                if default_style['bottom_margin'] != self.style['bottom_margin']:
                    points += self.weights['format']
                    format_bool[8] = True
            if self.style['right_margin'] is not None:
                if default_style['right_margin'] != self.style['right_margin']:
                    points += self.weights['format']
                    format_bool[9] = True
            if self.style['top_margin'] is not None:
                if default_style['top_margin'] != self.style['top_margin']:
                    points += self.weights['format']
                    format_bool[10] = True
            if self.style['header'] is not None:
                if default_style['header'] != self.style['header']:
                    points += self.weights['format']
                    format_bool[11] = True
            if self.style['footer'] is not None:
                if default_style['footer'] != self.style['footer']:
                    points += self.weights['format']
                    format_bool[12] = True
            if self.style['gutter'] is not None:
                if default_style['gutter'] != self.style['gutter']:
                    points += self.weights['format']
                    format_bool[13] = True
            if self.style['indent'] is not None:
                if self.style['indent'] < 0.5:
                    points += min(self.weights['format'] * (indent - self.style['indent']) * 2,
                                  self.weights['format'])
                else:
                    points += max(min(self.weights['format'] * (self.style['indent'] - indent) * 2,
                                      self.weights['format']), 0)
                if self.style['indent'] != indent:
                    format_bool[14] = True
            if self.style['left_margin'] is not None and self.style['right_margin'] is not None:
                points += min(self.weights['format'] * margin, self.weights['format'])
                if margin != 0:
                    format_bool[15] = True

            points = min(points, self.rubric['format'])
            debug += "Default Style: " + str(default_style) + "\nFonts: " + str(word.get_font_table()) + "\n"
            output += feedback.format_feedback(format_bool)

        return points, debug, output

    # This function will return the points lost, debug text, and feedback text in that order
    def grade_reference(self, text):
        points = 0
        debug, output = "", ""

        if self.rubric['reference'] is not None:
            reference = references.extract_citation(text)

            points = min(reference * self.weights['reference'], self.rubric['reference'])
            debug += "Number of Missing References: " + str(reference) + "\n"
            output += feedback.reference_feedback(round(points * 2 / self.rubric['reference']))

        return points, debug, output

    # Call this function to retrain the model
    def retrain_model(self, file_path, name=""):
        if name.lower() == "idea":
            print("--------IDEA---------")
            self.idea_model.train_and_test(file_path)
        if name.lower() == "organization":
            print("--------ORGANIZATION---------")
            self.organization_model.train_and_test(file_path)
        if name.lower() == "style":
            print("--------STYLE---------")
            self.style_model.train_and_test(file_path)
        if name.lower() != "idea" and name.lower() != "organization" and name.lower() != "style":
            self.model.train_and_test(file_path)

    # Change the style used while replacing the old style stored in the filepath if supplied
    def update_style(self, style, filepath=None):
        if set(style.keys()) == set(self.style.keys()):
            if filepath is not None:
                if not format.update_format_file(filepath, style):
                    return False
            self.style = style
            return True
        return False

    # Get the current style if no filepath is supplied, otherwise load another style
    def get_style(self, filepath=None):
        if filepath is not None:
            self.style = format.get_format_file(filepath)
        return self.style
