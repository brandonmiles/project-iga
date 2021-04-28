import pandas


class KeyWords:
    """
    The KeyWords class is used to search a given essay with a list of keywords and record their occurrences.
    It can also be used to add/remove words from a keyword list.

    Parameters
    ----------
    filepath : str
        An optional filepath to a .csv containing a list of keywords. Not providing a filepath means starting with an
        empty keyword list that can be filled in over time.
    """

    __slots__ = ('__filepath', '__keys')

    def __init__(self, filepath=None):  # Initialize with the dictionary file known
        self.__filepath = filepath
        self.__keys = []

        if filepath is not None:
            try:
                self.__keys = open(filepath, 'r').read().split(',')
            except FileNotFoundError:
                print(filepath, " not found")

    def occurrence(self, text):
        """
        Counts the occurrences of each keyword in a given essay

        Parameters
        ----------
         text : str
            This is the raw text that you want to check.

        Returns
        -------
        list
            This is a list of pairs, where each pair consists of the keyword followed by the number of occurrences of it
            in the text.
        """
        pair = []

        for i in self.__keys:  # Look for the keywords
            char_loc, number = 0, 0

            while True:
                char_loc = text.find(i, char_loc) + 1
                if char_loc == 0:
                    break
                else:
                    number += 1

            pair.append((i, number))

        return pair

    def get_keywords(self):
        """
        Returns
        -------
        list of str
            A list of all currently used keywords.
        """
        return self.__keys

    def add_keyword(self, word):
        """
        Adds given word to the current keyword list and to the corresponding .csv file

        Parameters
        ----------
        word : str
            This should be a single word to be added to the keywords

        Returns
        -------
        bool
            True if added successfully, False otherwise.
        """
        keys = self.__keys
        if word.lower() in keys:
            return True

        keys.append(word.lower())
        if self.filepath is not None:
            try:
                open(self.filepath, 'w').write(keys)
            except PermissionError:
                return False
        self.__keys = keys
        return True

    def remove_keyword(self, word):
        """
        Removes given word from the current keyword list and the corresponding .csv file.
        If the word doesn't exist in the keyword list, then simply return True.

        Parameters
        ----------
        word : str
            This should be a single word to be removed from the keywords

        Returns
        -------
        bool
            True if removed successfully, False otherwise.
        """
        keys = self.__keys
        if word.lower() not in keys:
            return True
        while word.lower() in keys:
            keys.remove(word.lower())

        if self.filepath is not None:
            try:
                open(self.filepath, 'w').write(keys)
            except FileNotFoundError:
                return False
        self.__keys = keys
        return True
