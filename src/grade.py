import grammar_check
import keywords
import feedback
import format
import references
from score_model import ScoreModel, IdeaModel, OrganizationModel, StyleModel
from pdfminer.high_level import extract_text
from pdfminer.utils import open_filename # Not used here, but might be needed for Sphinx build


# If you want to run this program specifically, you can put the appropriate
# code into this main() function.
def main():
    return


# This stops all the code from running when Sphinx imports the module.
if __name__ == '__main__':
    main()


def get_style():
    """
    Returns dictionary defining the essay's style

    Returns
    -------
    dict
        Please refer to format.py for the full description of the style dictionary keys.
    """
    return format.get_style()


def get_rubric():
    """
    Returns dictionary defining the essay's rubric

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
    Returns dictionary containing weights for each preference

    Returns
    -------
    dict
        The dictionary contains the following keys:\n
        'grammar' allows you to specify how many points are lost per grammar or spelling mistake.\n
        'allowed_mistakes' lets you specify how many grammar or spelling mistakes are allowed before points are lost.\n
        'key_max' is the expected number of different keywords the essay should have.\n
        'key_min' is how many keywords the essay need to have before they simply get zero points for the section.\n
        'word_min' is a measure of how many words are expected minimum or else they lose full points for the section.\n
        'word_max' is the maximum number of words an essay can have before losing half the points for the section.\n
        'page_min' same as word_min except if you want a different standard to judge word doc files.\n
        'page_max' as as word_max with the same exception as page_min.\n
        'format' represents how many points are lost for every formatting error; word doc only.\n
        'reference' is the number of points lost for every missing reference in the essay.\n
        Please note that allowed_mistakes, word_min, word_max, page_min, and page max can all be None if you don't wish
        to provide a value, but every other key must have an associated non-None integer value.
    """
    return {'grammar': 0, 'allowed_mistakes': 0, 'key_max': 0, 'key_min': 0, 'word_min': None,
            'word_max': None, 'page_min': None, 'page_max': None, 'format': 0, 'reference': 0}


def get_filepath():
    """
    Returns dictionary containing filepaths for data relevant to grading

    Returns
    -------
    dict
        The dictionary contains the following keys:\n
        'model' is a filepath to the score model's saved weights.\n
        'model_data' is a filepath to the score model's training data.\n
        'idea' is a filepath to the idea model's saved weights.\n
        'idea_data' is a filepath to the idea model's training data.\n
        'organization' is a filepath to the organization model's saved weights.\n
        'organization_data' is a filepath to the organization model's training data.\n
        'style' is a filepath to the style model's saved weights.\n
        'style_data' is a filepath to the style model's training data.\n
        'embedding' is a filepath to glove.6B.300d.txt.\n
        'style_json' is a filepath to a .json file where a style for format.py is stored.\n
        'dictionary' is a filepath to a .csv file containing the keywords to be used when grading papers. Can be set to
        None if you don't want to start with any keywords.
    """
    return {'model': 'model_weights/final_lstm.h5', 'model_data': '../data/training_set.tsv',
            'idea': 'model_weights/final_idea_lstm.h5', 'idea_data': '../data/comment_set.tsv',
            'organization': 'model_weights/final_organization_lstm.h5', 'organization_data': '../data/comment_set.tsv',
            'style': 'model_weights/final_style_lstm.h5', 'style_data': '../data/comment_set.tsv',
            'embedding': '../data/glove6B/glove.6B.300d.txt', 'style_json': '../data/standard.json',
            'dictionary': '../data/dictionary.csv'}


class Grade:
    """
    The Grade class contains definitions and functions used to grade an essay based on the given rubric and weights.
    The grade produced here is the final grade sent to the user.

    Parameters
    ----------
    rubric : dict
        rubric should be a dictionary with the same keys as grade.get_rubric(). rubric will be used to calculate exactly
        how many points each graded section is worth, and any graded section can be skipped by simply making a key
        equal to None.
    weights : dict
        weights should be a dictionary with the same keys as the grade.get_weights(). weights contains various alterable
        values that effect how each section is graded.
    start : str
        This is a relative filepath to the src folder location, where all other file paths are based off of.
    filepath : dict
        filepath should be a dictionary with the same keys as grade.get_filepath(). All file paths needed for grade to
        run properly can be found here, and should be the relative filepath from src.
    style : dict
        style should be a dictionary with the same keys as grade.get_style() or a filepath to a .json file which
        contains a style dictionary. This has a default value set, but if the file is missing, an Exception will be
        thrown.

    Raises
    ------
    KeyError
        Getting this error means that more likely than not, a passed in parameter was wrong, such as a dictionary not
        having the correct keys.
    FileNotFoundError
        If you get this, then one of the given file paths was incorrect or the file was simply missing.
    """

    __slots__ = ('__model', '__idea_model', '__organization_model', '__style_model', '__words', '__rubric', '__weights',
                 '__style', '__filepath')

    def __init__(self, rubric, weights, start, filepath=None, style=None):
        # Setting up file paths
        if type(filepath) is not dict:
            filepath = get_filepath()
        self.__filepath = get_filepath()
        for i in filepath.keys():
            self.__filepath[i] = start + filepath[i]

        # Creating the models
        self.__model = ScoreModel(self.__filepath['model'], self.__filepath['model_data'], self.__filepath['embedding'])
        self.__idea_model = IdeaModel(self.__filepath['idea'], self.__filepath['idea_data'],
                                      self.__filepath['embedding'])
        self.__organization_model = OrganizationModel(self.__filepath['organization'],
                                                      self.__filepath['organization_data'],
                                                      self.__filepath['embedding'], self.__idea_model.get_embedding())
        self.__style_model = StyleModel(self.__filepath['style'], self.__filepath['style_data'],
                                        self.__filepath['embedding'], self.__idea_model.get_embedding())

        # These are left empty until something is done otherwise
        self.__words = keywords.KeyWords()

        # Storing the given rubric if it is correct
        if type(rubric) is dict and set(rubric.keys()) == set(get_rubric().keys()):
            self.__rubric = rubric
        else:
            raise KeyError("Given rubric keys do not match skeleton keys")
        # Storing the given weights if it is correct
        if type(weights) is dict and set(weights) == set(get_weights().keys()):
            self.__weights = weights
        else:
            raise KeyError("Given weight keys do not match skeleton keys")
        # Storing the given style if it is correct or retrieving the given filepath
        if type(style) is dict:
            if set(style.keys()) == set(get_style().keys()):
                self.__style = style
            else:
                raise KeyError("Given style keys do not match skeleton keys")
        else:
            self.__style = format.get_format_file(self.__filepath['style_json'])
        # Getting the keyword list if a filepath was given
        if filepath['dictionary'] is not None:
            self.__words = keywords.KeyWords(self.__filepath['dictionary'])

    def get_grade(self, text):
        """
        Returns a grade for the given essay in line with the rubric

        Parameters
        ----------
        text : str
            This can either be raw essay text or a filepath to a .txt, .pdf, or .docx. it will assume that it was
            given a filepath if the the beginning of the string is either ./ or ../

        Returns
        -------
        tuple of str, int, str
            A tuple containing debug(string), points(integer), and feedback(string).
            Debug contains information from every section that was graded.
            Grade is on a scale of 0 - 100 that represents the final given grade. This value starts at 100 and has
            points taken off by each section until there is at minimum 0 left.
            Feedback contains all of the feedback information from every section that was graded.

        Raises
        ------
        FileNotFoundError
        The given filepath was either wrong, is missing, or is the wrong type.
		"""
        grade, page, word = 100, None, None
        debug, output, t = "", "", ""

        # text must be a filepath
        if len(text) > 3 and (text[0:3] == '../' or text[0:2] == './'):
            f = text.split('.')

            # File must be a docx
            if f[len(f) - 1] == "docx":
                word = format.Format(text)
                t = word.get_text()
                page = word.get_page_count()
            # File must be a pdf
            if f[len(f) - 1] == "pdf":
                t = extract_text(text)
                # PDF reader has trouble dealing with large line spacing, so this is an attempt to fix it.
                t = t.replace("\n\n", " ").replace("  ", " ").replace("  ", " ")
            # File must be a txt
            if f[(len(f) - 1)] == "txt":
                t = open(str(text), 'r').read()
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
        Returns a grade based on grammar and spelling in the given essay

        Parameters
        ----------
        text : str
            The raw text that will be checked for grammar and spelling mistakes

        Returns
        -------
        tuple of int, str, str
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
        Returns a grade based on the use (or disuse) of keywords in the given essay

        Parameters
        ----------
        text : str
            Preferably the corrected text from grade_grammar(), text will be searched for all of the currently defined
            keywords.

        Returns
        -------
        tuple of int, str, str
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
            points = max((self.__weights['key_max'] - key) / (self.__weights['key_max'] - self.__weights['key_min']),
                         0.0)
            points = min(round(points * self.__rubric['key']), self.__rubric['key'])
            debug += "Keyword Usage: " + str(key_list) + "\n"
            output += feedback.keyword_feedback(round(points * 3 / self.__rubric['key']))

        return points, debug, output

    def grade_length(self, text, page=None):
        """
        Returns a grade based on the length of the given essay

        Parameters
        ----------
        text : str
            Preferably the corrected text from grade_grammar(), the number of words contained in text will be used.
        page : int
            An int that a doc or docx may have that can be used in place of word count grading

        Returns
        -------
        tuple of int, str, str
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
        Returns a grade based on the outputs of the score and feedback models when given the input essay

        Parameters
        ----------
        text : str
            Preferably the corrected text from grade_grammar(), will be fed into all four models to be evaluated.

        Returns
        -------
        tuple of int, str, str
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
        Returns a grade based on the format of the given essay

        Parameters
        ----------
        word : format.Format
            An object generated by format when given a docx, will be read for its listed format

        Returns
        -------
        tuple of int, str, str
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

    def grade_reference(self, text):
        """
        Returns a grade based on the use (or disuse) of references in the given essay

        Parameters
        ----------
        text : str
            Preferably the corrected text from grade_grammar(), the text will be searched for any references.

        Returns
        -------
        tuple of int, str, str
            A tuple containing points(integer), debug(string), and feedback(string).
            Points is the number of points lost in this section, being between 0 and rubric['length'].
            Debug contains the number of missing references.
            Feedback will contain a pre-written string based on the number of points being taken off.
            See feedback.py for more info.
        """
        points = 0
        debug, output = "", ""

        if self.__rubric['reference'] is not None:
            reference = references.extract_citation(text)

            points = min(reference * self.__weights['reference'], self.__rubric['reference'])
            debug += "Number of Missing References: " + str(reference) + "\n"
            output += feedback.reference_feedback(round(points * 2 / self.__rubric['reference']))

        return points, debug, output

    def retrain_model(self, filepath=None, name="score"):
        """
        Retrains the score and feedback models

        Parameters
        ----------
        filepath : str
            This should be a file path to a .csv file containing the data to train the model with. If filepath is None,
            then the model will attempt to retrain itself based off the previously given data path.
        name : str
            This parameter specifies which model is to be retrained. Acceptable strings are 'score', 'idea',
            'organization', or 'style'.

        Returns
        -------
        bool
            Returns True if the model was trained successfully, otherwise False.
        """
        if name.lower() == "idea":
            return self.__idea_model.load_data(filepath)
        if name.lower() == "organization":
            return self.__organization_model.load_data(filepath)
        if name.lower() == "style":
            return self.__style_model.load_data(filepath)
        if name.lower() == "score":
            return self.__model.load_data(filepath)

    def update_style(self, style, filepath=None):
        """
        Updates current style and stores (possibly different) style at given filepath (if one is given)

        Parameters
        ----------
        style : dict
            Should match the dictionary given by calling grade.get_style().
        filepath : str
            If provided, the given style will be stored at the file location.

        Returns
        -------
        bool
            True if the given style was correct and was saved correctly if a filepath was given, otherwise False.
        """
        if type(style) is dict and set(style.keys()) == set(self.__style.keys()):
            if filepath is not None:
                if not format.update_format_file(filepath, style):
                    return False
            self.__style = style
            return True
        return False

    def get_style(self, filepath=None):
        """
        Returns current style and updates it if style file is given

        Parameters
        ----------
        filepath : str
            If supplied, the style found in the file will replace the currently used style.

        Returns
        -------
        dict
            A style dictionary, unless the style couldn't be loaded from the file, raises an Exception then.
        """
        if filepath is not None:
            self.__style = format.get_format_file(filepath)
        return self.__style

    def get_rubric(self):
        """
        Returns
        -------
        dict
            Gets the currently used rubric.
        """
        return self.__rubric

    def update_rubric(self, rubric):
        """
        Replaces the current rubric

        Parameters
        ----------
        rubric : dict
            Should be a dictionary with the same keys as grade.get_rubric().

        Returns
        -------
        bool
            If the supplied rubric is correct, return True, otherwise False.
        """
        if type(rubric) is dict and set(rubric.keys()) == set(get_rubric().keys()):
            self.__rubric = rubric
            return True
        return False

    def get_weights(self):
        """
        Returns
        -------
        dict
            The currently used weights dictionary.
        """
        return self.__weights

    def update_weights(self, weights):
        """
        Replaces the current weights

        Parameters
        ----------
        weights : dict
            Should match the keys given by grade.get_weights().

        Returns
        -------
        bool
            True if the given weights is correct, otherwise returns False.
        """
        if type(weights) is dict and set(weights) == set(get_weights().keys()):
            self.__weights = weights
            return True
        return False

    def get_keywords(self):
        """
        Returns
        -------
        list of str
            A list of the currently used keywords.
        """
        return self.__words.get_keywords()

    def add_keyword(self, word):
        """
        Adds given word to the keyword list and corresponding .csv file (if one was provided beforehand)

        Parameters
        ----------
        word : str
            A single word to be added to a list of words.

        Returns
        -------
        bool
            True if the word was added successfully to the list and dictionary file, otherwise False.
        """
        return self.__words.add_keyword(word)

    def remove_keyword(self, word):
        """
        Removes given word from the keyword list and corresponding .csv file (if one exists)

        Parameters
        ----------
        word : str
            A single word to be added to the keyword list

        True if removed successfully from both the list and .csv file, otherwise False.

        """
        return self.__words.remove_keyword(word)

    def clear_keywords(self):
        """
        Returns
        -------
        bool
            True if the word list is cleared completely
        """
        self.__words = keywords.KeyWords()
        return True
