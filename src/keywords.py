import pandas


class KeyWords:
    def __init__(self, filepath=None):  # Initialize with the dictionary file known
        self.filepath = filepath
        self.keys = []

        if filepath is not None:
            try:
                self.keys = open(filepath, 'r').read().split(',')
            except FileNotFoundError:
                print(filepath, " not found")

    # Given text, return a tuple of lists that contain the keywords and their occurrences
    def occurrence(self, text):
        pair = []

        for i in self.keys:  # Look for the keywords
            char_loc, number = 0, 0

            while True:
                char_loc = text.find(i, char_loc) + 1
                if char_loc == 0:
                    break
                else:
                    number += 1

            pair.append((i, number))

        return pair

    # Add a word to the key word dictionary
    def add_keyword(self, word):
        keys = self.keys
        if word.lower() in keys:
            return True

        try:
            keys = keys.append(word.lower())
            open(self.filepath, 'w').write(keys)
        except PermissionError:
            return False
        self.keys = keys
        return True

    # Remove a key word from the dictionary
    def remove_keyword(self, word):
        keys = self.keys
        while word.lower() in keys:
            keys.remove(word.lower())

        try:
            open(self.filepath, 'w').write(keys)
        except FileNotFoundError:
            return False
        self.keys = keys
        return True
