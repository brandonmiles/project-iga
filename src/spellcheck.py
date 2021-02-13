import nltk
import textblob
from nltk.corpus import wordnet
from nltk.corpus import stopwords
from textblob import Word

englishStop = set(stopwords.words('english'))


class SpellCheck:
    punctuation = {'.', ',', '?', '!', '>', '<', '/', '\'', '\'\'', '\"', ':', ';', '+', '=', '-', '_', '*', '&', '(',
                   ')', '~', '`'}  # Feel free to add to alter the list of allowable punctuation
    exceptions = []
    file_name = ''

    def __init__(self, file_name):
        self.file_name = file_name
        exception_file = open(self.file_name, 'r')
        for line in exception_file:
            self.exceptions.append(line.rstrip().lower())

    # Given a list of tokens, return a tuple of the number of errors and the misspelled words in question
    def number_of_errors(self, tokens):
        count = 0
        misspell = ''

        for i in tokens:
            j = i.rstrip().lower()
            if j not in self.punctuation:  # Punctuation filter
                if not j.isdigit():  # Number filter
                    if j not in self.exceptions:  # Exceptions filter
                        if j not in englishStop:  # First word filter
                            if not wordnet.synsets(j):  # Second word filter
                                if not j == Word(j).spellcheck()[0][0]:  # Third word filter
                                    count += 1
                                    misspell += j + ' '
        return count, misspell.rstrip()

    def add_exception(self, word):
        if word.lower() in self.exceptions:
            return True
        try:
            exception_file = open(self.file_name, 'a')
            exception_file.write(word.lower() + '\n')
            self.exceptions.append(word.lower())
        except FileNotFoundError:
            return False
        return True
