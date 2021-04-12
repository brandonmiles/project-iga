import grammar_check
import keywords
import feedback
import format
import references
from feedback_model import ScoreModel, IdeaModel, OrganizationModel, StyleModel
from pdfminer.high_level import extract_text

# Every key represents an area where points can be lost on the essay, by leaving a key as None, the section will not be
# graded, changing it to an int will cause a maximum amount of the int number of points to be taken off
RUBRIC_SKELETON = {'grammar': None, 'key': None, 'length': None, 'format': None, 'model': None, 'reference': None}

WEIGHTS_SKELETON = {'grammar': None,  # How many points are lost for every grammar and spelling mistake
                    'allowed_mistakes': None,  # How many grammar and spelling mistakes are allowed before losing points
                    'key_max': None,  # The number of key words needed to get full credit
                    'key_min': None,  # The number of key words at minimum are needed before you lose all credit
                    'word_min': None,  # The number of words minimum needed or else you lose all credit
                    'word_max': None,  # The number of words maximum before you lose half credit
                    'page_min': None,  # The number of pages minimum before you lose all credit, only applicable to docx
                    'page_max': None,
                    'format': None,  # The number of points lost for every format error, only applicable to docx
                    'reference': None}  # The number of points lost for every missing reference


# Use to get the dictionary structure that defines the style
def get_style():
    return format.get_style()


# Use to get the dictionary structure that defines the rubric
def get_rubric():
    return RUBRIC_SKELETON


# Use to get the dictionary structure that defines the rubric
def get_weights():
    return WEIGHTS_SKELETON


class Grade:
    # Technically the last field can be voided if you are either not grading format or only using the raw text function
    def __init__(self, rubric, weights, dictionary_path='../data/dictionary.csv', style=None,
                 style_path='../data/standard.json'):
        # Creating the models
        self.model = ScoreModel()
        self.idea_model = IdeaModel()
        self.organization_model = OrganizationModel()
        self.style_model = StyleModel()
        # These are left empty until something is done otherwise
        self.style = get_style()
        self.words = keywords.KeyWords()

        # Storing the given rubric if it is correct
        if set(rubric.keys()) == set(RUBRIC_SKELETON.keys()):
            self.rubric = rubric
        else:
            raise Exception("Given rubric keys do not match skeleton keys")
        # Storing the given weights if it is correct
        if set(weights) == set(WEIGHTS_SKELETON.keys()):
            self.weights = weights
        else:
            raise Exception("Given weight keys do not match skeleton keys")
        # Storing the given style if it is correct or retrieving the file
        if style is not None:
            if set(style.keys() == set(STYLE_SKELETON.keys())):
                self.style = style
            else:
                raise Exception("Given style keys do not match skeleton keys")
        else:
            if style_path is not None:
                self.style = format.get_format_file(style_path)
        # Getting the keyword list if a file path was given
        if dictionary_path is not None:
            try:
                self.words = keywords.KeyWords(dictionary_path)
            except FileNotFoundError:
                print(str(dictionary_path) + " not found")

    # Specify whether you are giving raw text or a file path, will return the debug, grade, and output in that order
    def get_grade(self, text=None, filepath=None):
        grade, page, word = 100, None, None
        debug, output, t = "", "", ""

        # You cannot give both or neither raw text and filepath
        if (text is None and filepath is None) or (text is not None and filepath is not None):
            return None, None, None

        # If no text is given, then the filepath was
        if text is not None:
            t = text
        else:
            f = filepath.split('.')

            # File must be a docx or doc
            if f[len(f) - 1] == "docx" or f[len(f) - 1] == "doc":
                try:
                    word = format.Format(filepath)
                    t = word.get_text()
                    page = word.get_page_count()
                except FileNotFoundError:
                    return None, None, None
            # File must be a pdf
            if f[len(f) - 1] == "pdf":
                try:
                    t = extract_text(filepath)
                    # PDF reader has trouble dealing with large line spacing, so this is an attempt to fix it.
                    t = t.replace("\n\n", " ").replace("  ", " ").replace("  ", " ")
                except FileNotFoundError:
                    return None, None, None
            # File must be a txt
            if f[f(len(f) - 1)] == "txt":
                try:
                    t = open(str(filepath), 'r').read()
                except FileNotFoundError:
                    return None, None, None

        # Run the grammar and spelling check
        p, corrected_text, d, o = self.grade_grammar(t)
        grade -= p
        debug += d
        output += o

        # Run the keyword check
        p, d, o = self.grade_key(corrected_text)
        grade -= p
        debug += d
        output += o

        # Run the length check
        p, d, o = self.grade_length(corrected_text, page)
        grade -= p
        debug += d
        output += o

        # Run the format check
        p, d, o = self.grade_format(word)
        grade -= p
        debug += d
        output += o

        # Run the model check
        p, d, o = self.grade_model(corrected_text)
        grade -= p
        debug += d
        output += o

        # Run the reference check
        p, d, o = self.grade_reference(corrected_text)
        grade -= p
        debug += d
        output += o

        return debug, max(grade, 0), output

    # This function will return the points lost, corrected text, debug text, and feedback text in that order
    def grade_grammar(self, text):
        points = 0
        debug, output = "", ""

        # Need corrected text for other functions, so always run
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
    def retrain_model(self, filepath, name="score"):
        if name.lower() == "idea":
            self.idea_model.load_data(filepath)
        if name.lower() == "organization":
            self.organization_model.load_data(filepath)
        if name.lower() == "style":
            self.style_model.load_data(filepath)
        if name.lower() == "score":
            self.model.load_data(filepath)

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

    def get_rubric(self):
        return self.rubric

    def update_rubric(self, rubric):
        if set(rubric.keys()) == set(RUBRIC_SKELETON.keys()):
            self.rubric = rubric
            return True
        return False

    def get_weights(self):
        return self.weights

    def update_weights(self, weights):
        if set(weights) == set(WEIGHTS_SKELETON.keys()):
            self.weights = weights
            return True
        return False

    def get_keywords(self):
        return self.words

    def add_keyword(self, word):
        return self.words.add_keyword(word)

    def remove_keyword(self, word):
        return self.words.remove_keyword(word)

    def clear_keywords(self):
        self.words = keywords.KeyWords()
        return True
