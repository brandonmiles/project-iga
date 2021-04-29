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

    Raises
    ------
    TypeError
        You can only get this exception if you attempt to pass in a non-string value into init.
    FileNotFoundError
        You will get this if the given filepath points to a non-existent file.
    PermissionError
        You will get this if you don't have permission to read folder/file given in filepath.
    """

    __slots__ = ('__filepath', '__keys')

    def __init__(self, filepath=None):  # Initialize with the dictionary file known
        self.__filepath = filepath
        self.__keys = []

        if filepath is not None:
            if type(filepath) is not str:
                raise TypeError("filepath must be a string that represents a filepath.")
            file = open(filepath, 'r')
            self.__keys = file.read().split(',')
            while '' in self.__keys:
                self.__keys.remove('')
            file.close()

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

        Raises
        ------
        TypeError
            text should be a string
        """
        pair = []

        if type(text) is not str:
            raise TypeError("text should be a string")

        text = text.lower()
        text_list = text.split(' ')

        for i in self.__keys:  # Look for the keywords
            number = 0

            while i in text_list:
                number += 1
                text_list.remove(i)

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
            True if added successfully.

        Raises
        ------
        PermissionError
            Could not overwrite existing filepath
        TypeError
            word should be a single word string
        """
        if type(word) is not str:
            raise TypeError("word should be a single word string")

        keys = self.__keys
        if word.lower() in keys:
            return True
        keys.append(word.lower())

        key_str = ''
        for i in keys:
            key_str += i + ','
        key_str = key_str.strip(',')

        if self.__filepath is not None:
            file = open(self.__filepath, 'w')
            file.write(key_str)
            file.close()
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
            True if removed successfully.

        Raises
        ------
        PermissionError
            Could not write over the given filepath
        TypeError
            word should be a single word string
        """
        if type(word) is not str:
            raise TypeError("word should be a single word string")

        keys = self.__keys
        if word.lower() not in keys:
            return True
        while word.lower() in keys:
            keys.remove(word.lower())

        key_str = ''
        for i in keys:
            key_str += i + ','
        key_str = key_str.strip(',')

        if self.__filepath is not None:
            file = open(self.__filepath, 'w')
            file.write(key_str)
            file.close()

        self.__keys = keys
        return True
