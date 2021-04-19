import grammar_check
import keywords
import feedback
import format
import references
from score_model import ScoreModel, IdeaModel, OrganizationModel, StyleModel
from pdfminer.high_level import extract_text


def get_style():
    """
    Use to get the dictionary structure that defines the style.

    Returns
    -------
    dict
        Please refer to format.py for the full description of the style dictionary keys.
    """
    return format.get_style()


def get_rubric():
    """
    Use to get the dictionary structure that defines the rubric.

    Returns
    -------
    dict
        There are six total sections, including grammar and spelling, keyword usage, length of the essay, format of the
        essay, the grade the model assigns the essay, and the number of references missing. Note that the format section
        will only be graded if a doc or docx is being used, as neither txt, pdf, or raw text support formatting.
    """
    return {'grammar': None, 'key': None, 'length': None, 'format': None, 'model': None, 'reference': None}


def get_weights():
    """
    Use to get the dictionary structure that defines the weights.

    Returns
    -------
    dict
        The dictionary contains the following keys:
        'grammar' allows you to specify how many points are lost per grammar or spelling mistake.
        'allowed_mistakes' lets you specify how many grammar or spelling mistakes are allowed before points are lost.
        'key_max' is the expected number of different keywords the essay should have.
        'key_min' is how many keywords the essay need to have before they simply get zero points for the section.
        'word_min' is a measure of how many words are expected minimum or else they lose full points for the section.
        'word_max' is the maximum number of words an essay can have before losing half the points for the section.
        'page_min' same as word_min except if you want a different standard to judge word doc files.
        'page_max' as as word_max with the same exception as page_min.
        'format' represents how many points are lost for every formatting error, word doc only.
        'reference' is the number of points lost for every missing reference in the essay.
        Please Note that allowed_mistakes, word_min, word_max, page_min, and page max can all be None if you don't wish
        to provide a value, but every other key must have an associated non-None integer value.
    """
    return {'grammar': 0, 'allowed_mistakes': 0, 'key_max': 0, 'key_min': 0, 'word_min': None,
            'word_max': None, 'page_min': None, 'page_max': None, 'format': 0, 'reference': 0}


class Grade:
    """
    This class is used to actually grade an essay based on the given rubric and weights.

    Parameters
    ----------
    rubric : dict
        rubric should be a dictionary with the same keys as the RUBRIC_SKELETON that can be gotten with
        grade.get_rubric(). rubric will be used to calculate exactly how many points each graded section is worth, and
        any graded section can be skipped by simply making a key equal to None.
        This is a required parameter to initialize Grade().
    weights : dict
        weights should be a dictionary with the same keys as the WEIGHTs_SKELETON that can be gotten with
        grade.get_weights(). weights contains various alterable values that effect how each section is graded.
        This is a required parameter to initialize Grade().
    dictionary_path : str
        This should be the filepath to a .csv file, which contains a list of keywords that will be searched for in the
        essay. It does have a default value, but you may set the path to None instead if you wish to not start with a
        set of keywords and instead have an empty set that can be slowly added and removed from.
        Not a required parameter.
    style : dict
        style should be a dictionary with the same keys as the STYLE_SKELETON that can be gotten with grade.get_style()
        or a filepath to a .json file which contains a style dictionary. This has a default value set, but if the file
        is missing, an Exception will be thrown.

    Raises
    ------
    Exception
        A variety of generic exceptions each with their own associated text to describe the error.
    """

    # Technically the last field can be voided if you are either not grading format or only using the raw text function
    def __init__(self, rubric, weights, dictionary_path='../data/dictionary.csv', style='../data/standard.json'):
        # Creating the models
        self.__model = ScoreModel()
        self.__idea_model = IdeaModel()
        self.__organization_model = OrganizationModel(self.__idea_model.get_embedding())
        self.__style_model = StyleModel(self.__idea_model.get_embedding())
        # These are left empty until something is done otherwise
        self.__words = keywords.KeyWords()

        # Storing the given rubric if it is correct
        if set(rubric.keys()) == set(get_rubric().keys()):
            self.__rubric = rubric
        else:
            raise Exception("Given rubric keys do not match skeleton keys")
        # Storing the given weights if it is correct
        if set(weights) == set(get_weights().keys()):
            self.__weights = weights
        else:
            raise Exception("Given weight keys do not match skeleton keys")
        # Storing the given style if it is correct or retrieving the given filepath
        if type(style) is str:
            style = format.get_format_file(style)
        if type(style) is dict:
            if set(style.keys()) == set(get_style().keys()):
                self.__style = style
            else:
                raise Exception("Given style keys do not match skeleton keys")
        else:
            raise Exception("Given style not a is dict or a filepath")
        # Getting the keyword list if a filepath was given
        if dictionary_path is not None:
            try:
                self.__words = keywords.KeyWords(dictionary_path)
            except FileNotFoundError:
                raise Exception(str(dictionary_path) + " not found")

    def get_grade(self, text):
        """
        This will grade every section in the given rubric

        Parameters
        ----------
        text : str
            This can either be raw essay text or a filepath to a .txt, .pdf, .doc, or .docx. it will assume that it was
            given a filepath if the the beginning of the string is either ./ or ../

        Returns
        -------
        tuple
            A tuple containing debug(string), points(integer), and feedback(string).
            Debug contains information from every section that was graded.
            Grade is on a scale of 0 - 100 that represents the final given grade. This value starts at 100 and has
             points taken off by each section until there is at minimum 0 left.
            Feedback contains all of the feedback information from every section that was graded.
        """
        grade, page, word = 100, None, None
        debug, output, t = "", "", ""

        # text must be a filepath
        if len(text) > 3 and (text[0:3] == '../' or text[0:2] == './'):
            f = text.split('.')

            # File must be a docx or doc
            if f[len(f) - 1] == "docx" or f[len(f) - 1] == "doc":
                try:
                    word = format.Format(text)
                    t = word.get_text()
                    page = word.get_page_count()
                except FileNotFoundError:
                    return None, None, None
            # File must be a pdf
            if f[len(f) - 1] == "pdf":
                try:
                    t = extract_text(text)
                    # PDF reader has trouble dealing with large line spacing, so this is an attempt to fix it.
                    t = t.replace("\n\n", " ").replace("  ", " ").replace("  ", " ")
                except FileNotFoundError:
                    return None, None, None
            # File must be a txt
            if f[(len(f) - 1)] == "txt":
                try:
                    t = open(str(text), 'r').read()
                except FileNotFoundError:
                    return None, None, None
        else:
            t = text

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

    def grade_grammar(self, text):
        """
        Use to grade only the grammar and spelling of a given text.

        Parameters
        ----------
        text : str
            The raw text that will be checked for grammar and spelling mistakes

        Returns
        -------
        tuple
            A tuple containing points(integer), corrected_text(string), debug(string), and feedback(string).
            Points is the number of points lost in this section, being between 0 and rubric['grammar'].
            Corrected_text is the given after being corrected for grammar and spelling mistakes. It is recommended that
             this is used in place of the original text when grading the other sections.
            Debug will contain the number of grammar and spelling mistakes in the text, followed by a list of pairs,
             where each pair contains the mistake and the suggested correction.
            Feedback will contain a pre-written string based on the number of points being taken off.
            See feedback.py for more info.
        """
        points = 0
        debug, output = "", ""

        # Need corrected text for other functions, so always run
        corrections, corrected_text = grammar_check.number_of_errors(text)
        if self.__rubric['grammar'] is not None:
            mistakes = len(corrections)
            if self.__weights['allowed_mistakes'] is not None:
                mistakes = max(mistakes - self.__weights['allowed_mistakes'], 0)

            points = min(self.__weights['grammar'] * mistakes, self.__rubric['grammar'])
            debug += "Errors: " + str(len(corrections)) + "\n"
            debug += str(corrections) + "\n"
            output += feedback.grammar_feedback(round(points * 3 / self.__rubric['grammar']))

        return points, corrected_text, debug, output

    def grade_key(self, text):
        """
        Use to grade only the keyword section.

        Parameters
        ----------
        text : str
            Preferably the corrected text from grade_grammar(), text will be searched for all of the currently defined
            keywords.

        Returns
        -------
        tuple
            A tuple containing points(integer), debug(string), and feedback(string).
            Points is the number of points lost in this section, being between 0 and rubric['key'].
            Debug contains a list of pairs, where each pair is the keyword and the number of occurrences of said keyword
             in the given text.
            Feedback will contain a pre-written string based on the number of points being taken off.
            See feedback.py for more info.
        """
        points, key = 0, 0
        debug, output = "", ""

        if self.__rubric['key'] is not None:
            key_list = self.__words.occurrence(text)
            for i in key_list:
                if i[1] > 0:
                    key += 1
            points = max((self.__weights['key_max'] - key) / (self.__weights['key_max'] - self.__weights['key_min']), 0.0)
            points = min(round(points * self.__rubric['key']), self.__rubric['key'])
            debug += "Keyword Usage: " + str(key_list) + "\n"
            output += feedback.keyword_feedback(round(points * 3 / self.__rubric['key']))

        return points, debug, output

    def grade_length(self, text, page=None):
        """
        Use to grade only the length section.

        Parameters
        ----------
        text : str
            Preferably the corrected text from grade_grammar(), the number of words contained in text will be used.
        page : int
            An int that a doc or docx may have that can be used in place of word count grading

        Returns
        -------
        tuple
            A tuple containing points(integer), debug(string), and feedback(string).
            Points is the number of points lost in this section, being between 0 and rubric['length'].
            Debug contains the number of words as well as the number of pages if applicable.
            Feedback will contain a pre-written string based on the number of points being taken off.
            See feedback.py for more info.
        """
        points = 0
        debug, output = "", ""

        count = len(text.split())
        if self.__rubric['length'] is not None:
            if self.__weights['page_min'] is not None and page is not None and page < self.__weights['page_min']:
                points = self.__rubric['length']
            if self.__weights['page_max'] is not None and page is not None and page > self.__weights['page_max']:
                points = round(self.__rubric['length'] / 2)
            if self.__weights['word_min'] is not None and page is None and count < self.__weights['word_min']:
                points = self.__rubric['length']
            if self.__weights['word_max'] is not None and page is None and count > self.__weights['word_max']:
                points = round(self.__rubric['length'] / 2)

            if page is not None:
                debug += "Page Count: " + str(page) + "\n"
            debug += "Word Count: " + str(count) + "\n"
            output += feedback.length_feedback(round(points * 2 / self.__rubric['length']))

        return points, debug, output

    def grade_model(self, text):
        """
        Use to grade only the model section.

        Parameters
        ----------
        text : str
            Preferably the corrected text from grade_grammar(), will be fed into all four models to be evaluated.

        Returns
        -------
        tuple
            A tuple containing points(integer), debug(string), and feedback(string).
            Points is the number of points lost in this section, being between 0 and rubric['model'].
            Debug the score given by the score model, idea model, organization model, and style model.
            Feedback will contain a pre-written string based on the score given by the three feedback models.
            See feedback.py for more info.
        """
        points = 0
        debug, output = "", ""

        if self.__rubric['model'] is not None:
            points = self.__model.evaluate(text)
            idea_score = round((self.__idea_model.evaluate(text) * 3) + 0.5) - 1
            organization_score = round((self.__organization_model.evaluate(text) * 3) + 0.5) - 1
            style_score = round((self.__style_model.evaluate(text) * 3) + 0.5) - 1

            debug += "Model Score: " + str(points) + "\n"
            points = round(self.__rubric['model'] * (1 - points))
            debug += "Idea Score: " + str(idea_score) + "\n"
            debug += "Organization Score: " + str(organization_score) + "\n"
            debug += "Style Score: " + str(style_score) + "\n"
            output += feedback.idea_feedback(idea_score)
            output += feedback.organization_feedback(organization_score)
            output += feedback.style_feedback(style_score)

        return points, debug, output

    def grade_format(self, word):
        """
        Use to grade only the format section.

        Parameters
        ----------
        word : format.Format
            An object generated by format when given a doc or docx, will be read for its listed format

        Returns
        -------
        tuple
            A tuple containing points(integer), debug(string), and feedback(string).
            Points is the number of points lost in this section, being between 0 and rubric['format'].
            Debug will contain the file's default style and font table.
            Feedback will contain a pre-written string based on every format mistake.
            See feedback.py for more info.
        """
        points = 0
        debug, output = "", ""
        format_bool = [False] * 16

        if self.__rubric['format'] is not None and word is not None:
            fonts = word.get_font()
            spacing = word.get_spacing()
            indent = word.get_indentation()
            margin = word.get_margin()
            default_style = word.get_default_style()

            if self.__style['font'] is not None:
                for f in fonts:
                    if f[0] not in self.__style['font']:
                        points += self.__weights['format']
                        format_bool[0] = True
            if self.__style['size'] is not None:
                for f in fonts:
                    if f[1] != self.__style['size']:
                        points += self.__weights['format']
                        format_bool[1] = True
            if self.__style['line_spacing'] is not None:
                for s in spacing:
                    if s[0] != self.__style['line_spacing']:
                        points += self.__weights['format']
                        format_bool[2] = True
            if self.__style['after_spacing'] is not None:
                for s in spacing:
                    if s[1] != self.__style['after_spacing']:
                        points += self.__weights['format']
                        format_bool[3] = True
            if self.__style['before_spacing'] is not None:
                for s in spacing:
                    if s[2] != self.__style['before_spacing']:
                        points += self.__weights['format']
                        format_bool[4] = True
            if self.__style['page_width'] is not None:
                if default_style['page_width'] != self.__style['page_width']:
                    points += self.__weights['format']
                    format_bool[5] = True
            if self.__style['page_height'] is not None:
                if default_style['page_height'] != self.__style['page_height']:
                    points += self.__weights['format']
                    format_bool[6] = True
            if self.__style['left_margin'] is not None:
                if default_style['left_margin'] != self.__style['left_margin']:
                    points += self.__weights['format']
                    format_bool[7] = True
            if self.__style['bottom_margin'] is not None:
                if default_style['bottom_margin'] != self.__style['bottom_margin']:
                    points += self.__weights['format']
                    format_bool[8] = True
            if self.__style['right_margin'] is not None:
                if default_style['right_margin'] != self.__style['right_margin']:
                    points += self.__weights['format']
                    format_bool[9] = True
            if self.__style['top_margin'] is not None:
                if default_style['top_margin'] != self.__style['top_margin']:
                    points += self.__weights['format']
                    format_bool[10] = True
            if self.__style['header'] is not None:
                if default_style['header'] != self.__style['header']:
                    points += self.__weights['format']
                    format_bool[11] = True
            if self.__style['footer'] is not None:
                if default_style['footer'] != self.__style['footer']:
                    points += self.__weights['format']
                    format_bool[12] = True
            if self.__style['gutter'] is not None:
                if default_style['gutter'] != self.__style['gutter']:
                    points += self.__weights['format']
                    format_bool[13] = True
            if self.__style['indent'] is not None:
                if self.__style['indent'] < 0.5:
                    points += min(self.__weights['format'] * (indent - self.__style['indent']) * 2,
                                  self.__weights['format'])
                else:
                    points += max(min(self.__weights['format'] * (self.__style['indent'] - indent) * 2,
                                      self.__weights['format']), 0)
                if self.__style['indent'] != indent:
                    format_bool[14] = True
            if self.__style['left_margin'] is not None and self.__style['right_margin'] is not None:
                points += min(self.__weights['format'] * margin, self.__weights['format'])
                if margin != 0:
                    format_bool[15] = True

            points = min(points, self.__rubric['format'])
            debug += "Default Style: " + str(default_style) + "\nFonts: " + str(word.get_font_table()) + "\n"
            output += feedback.format_feedback(format_bool)

        return points, debug, output

    # This function will return the points lost, debug text, and feedback text in that order
    def grade_reference(self, text):
        points = 0
        debug, output = "", ""

        if self.__rubric['reference'] is not None:
            reference = references.extract_citation(text)

            points = min(reference * self.__weights['reference'], self.__rubric['reference'])
            debug += "Number of Missing References: " + str(reference) + "\n"
            output += feedback.reference_feedback(round(points * 2 / self.__rubric['reference']))

        return points, debug, output

    # Call this function to retrain the model
    def retrain_model(self, filepath, name="score"):
        if name.lower() == "idea":
            self.__idea_model.load_data(filepath)
        if name.lower() == "organization":
            self.__organization_model.load_data(filepath)
        if name.lower() == "style":
            self.__style_model.load_data(filepath)
        if name.lower() == "score":
            self.__model.load_data(filepath)

    # Change the style used while replacing the old style stored in the filepath if supplied
    def update_style(self, style, filepath=None):
        if set(style.keys()) == set(self.__style.keys()):
            if filepath is not None:
                if not format.update_format_file(filepath, style):
                    return False
            self.__style = style
            return True
        return False

    # Get the current style if no filepath is supplied, otherwise load another style
    def get_style(self, filepath=None):
        if filepath is not None:
            self.__style = format.get_format_file(filepath)
        return self.__style

    def get_rubric(self):
        return self.__rubric

    def update_rubric(self, rubric):
        if set(rubric.keys()) == set(get_rubric().keys()):
            self.__rubric = rubric
            return True
        return False

    def get_weights(self):
        return self.__weights

    def update_weights(self, weights):
        if set(weights) == set(get_weights().keys()):
            self.__weights = weights
            return True
        return False

    def get_keywords(self):
        return self.__words

    def add_keyword(self, word):
        return self.__words.add_keyword(word)

    def remove_keyword(self, word):
        return self.__words.remove_keyword(word)

    def clear_keywords(self):
        self.__words = keywords.KeyWords()
        return True
