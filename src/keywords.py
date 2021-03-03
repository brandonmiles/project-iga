import pandas


class KeyWords:
    punctuation = {}
    file_name = ''
    kw = pandas.DataFrame({'words': []})

    def __init__(self, file_name, punctuation_list):  # Initialize with the dictionary file known
        self.file_name = file_name
        self.punctuation = punctuation_list

        try:
            self.kw = pandas.read_csv(file_name, sep='\t')
        except FileNotFoundError:
            print("Can't find ", file_name)

    def occurrence(self, text):  # Given text, return a tuple of lists that contain the keywords and their occurrences
        clean = []

        tokens = text.split()

        for i in range(len(tokens)):  # Checks the text and removes punctuation
            if tokens[i][0] in self.punctuation:
                tokens[i] = tokens[i][1:]
            for j in range(len(tokens[i])):
                if tokens[i][j] in self.punctuation:
                    tokens[i] = tokens[i].split(tokens[i][j])[0]
                    break
            if tokens[i] != '' and tokens[i][0] != '@':
                clean.append(tokens[i].lower())

        number = [0] * len(clean)

        for i in clean:  # Look for the keywords
            for j in range(len(self.kw['words'])):
                if i == self.kw['words'][j]:
                    number[j] = number[j] + 1
        return self.kw['words'], number

    # Add a word to the key word dictionary
    def add_keyword(self, word):
        if word.lower() in self.kw['words']:
            return True
        try:
            new_row = {'words': word.lower()}
            self.kw = self.kw.append(new_row, ignore_index=True)
            self.kw.to_csv(self.file_name, index=False, sep="\t", na_rep='', header=True, mode='w', decimal='.')
        except FileNotFoundError:
            return False
        return True
