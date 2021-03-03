import pandas


class KeyWords:
    file_name = ''
    kw = pandas.DataFrame({'words': []})

    def __init__(self, file_name):  # Initialize with the dictionary file known
        self.file_name = file_name

        try:
            self.kw = pandas.read_csv(file_name, sep='\t')
        except FileNotFoundError:
            print("Can't find ", file_name)

    # Given text, return a tuple of lists that contain the keywords and their occurrences
    def occurrence(self, text):
        pair = []

        for i in self.kw['words']:  # Look for the keywords
            char_loc = 0
            number = 0

            while True:
                char_loc = text.find(i, char_loc) + 1
                if char_loc == 0:
                    break
                else:
                    number = number + 1

            pair.append((i, number))

        return pair

    # Add a word to the key word dictionary
    def add_keyword(self, word):
        for i in self.kw.index:
            if word.lower() == self.kw['words'][i]:
                return True

        try:
            self.kw = self.kw.append({'words': word.lower()}, ignore_index=True)
            self.kw.to_csv(self.file_name, index=False, sep="\t", na_rep='', header=True, mode='w', decimal='.')
        except FileNotFoundError:
            return False
        return True

    # Remove a key word from the dictionary
    def remove_keyword(self, word):
        try:
            for i in self.kw.index:
                if word.lower() == self.kw['words'][i]:
                    self.kw = self.kw.drop(i, axis=0)
                    self.kw.to_csv(self.file_name, index=False, sep="\t", na_rep='', header=True, mode='w', decimal='.')
                    break
        except FileNotFoundError:
            return False
        return True
