import pandas
import nltk
import textblob
from nltk.corpus import wordnet
from nltk.corpus import stopwords
from textblob import Word

englishStop = set(stopwords.words('english'))


class SpellCheck:
    punctuation = {}
    exceptions = pandas.DataFrame({'token': [], 'token_type': []})
    file_name = ''

    def __init__(self, file_name, punctuation_list):  # Initialize with the exception file known
        self.file_name = file_name
        self.punctuation = punctuation_list

        try:
            self.exceptions = pandas.read_csv(file_name, sep='\t')
        except FileNotFoundError:
            print("Can't find ", file_name)

    # Given a list of tokens, return a tuple of the number of errors and the misspelled words in question
    def number_of_errors(self, text):
        count = 0
        misspell = ''
        clean = []

        tokens = text.split()

        for i in range(len(tokens)):  # Checks the text and removes punctuation and digits
            if tokens[i][0] in self.punctuation:
                tokens[i] = tokens[i][1:]
            if tokens[i].isdigit():
                continue
            for j in range(len(tokens[i])):
                if tokens[i][j] in self.punctuation:
                    tokens[i] = tokens[i].split(tokens[i][j])[0]
                    break
            if tokens[i] != '' and tokens[i][0] != '@':
                clean.append(tokens[i].lower())

        for i in clean:  # Actually start running through the spelling filters
            if i not in self.exceptions['token']:  # Exceptions filter
                if i not in englishStop:  # First word filter
                    if not i == Word(i).spellcheck()[0][0]:  # Second word filter
                        if not wordnet.synsets(i):  # Third word filter
                            count += 1
                            misspell += i + ' '
        return count, misspell.rstrip()

    # Need not only the word, but also what the word is, i.e. a noun, verb, etc.
    def add_exception(self, word, token_type):
        if word.lower() in self.exceptions['token']:
            return True
        try:
            new_row = {'token': word.lower(), 'token_type': token_type}
            self.exceptions = self.exceptions.append(new_row, ignore_index=True)
            self.exceptions.to_csv(self.file_name, index=False, sep="\t", na_rep='', header=True, mode='w', decimal='.')
        except FileNotFoundError:
            return False
        return True
