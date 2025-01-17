from abc import ABC, abstractmethod
from keras.layers import LSTM, Dense, Embedding, GlobalMaxPooling1D
from keras.models import Sequential
from keras.preprocessing.text import Tokenizer
from keras.preprocessing.sequence import pad_sequences
import numpy as np
import pandas
import os
import score_model_helper
from sklearn.model_selection import KFold


class Model(ABC):
    """
    The Model class is an abstract class that should NOT be initialized, but only used to define the variables and
    functions used by the other model classes.
    """
    __slots__ = ('_tokenizer', '_model', '_vocab_size', '_filepath', '_embedding', '__data_path')

    def __init__(self):
        self._tokenizer = Tokenizer()
        self._model = Sequential()
        self._vocab_size = None
        self._filepath = None
        self._embedding = None
        self.__data_path = None

    @abstractmethod
    def load_data(self, filepath=None):
        """
        The load_data function needs to be replaced by any inheriting classes. This function should should create an 'x'
        pandas Dataframe that contains an 'essays' column as well as a y pandas Dataframe that contains the same
        indexes as x and a 'normal' column that represents the normalized scores of the x essays.

        Parameters
        ----------
        filepath : str
            This should be a filepath to a .csv file containing the data to train the model
        """
        pass

    def get_embedding(self):
        """
        Returns
        -------
        numpy.ndarray
            An embedding matrix to be used between models with the same parameters in order to reduce load times.
        """
        return self._embedding

    def train_and_test(self, x, y, n_splits, epochs):
        """
        Trains the model so it can be used to evaluate essays. The model's filepath will be used to save the
        weights of the model at the end of training. Progress will be output with relevant information about the
        accuracy of the model as it is being trained.

        Parameters
        ----------
        x : pandas.Dataframe
            Should be a dataframe containing a 'essay' column to train the model with.
        y : pandas.Dataframe
            Should be a dataframe with the same indexes as x and a 'normal' column whose type is float32, being between
            0.0 and 1.0.
        n_splits : int
            How many folds the model will train for.
        epochs : int
            How many epochs the model will go through for each fold.

        Returns
        -------
        bool
            True if the training was successful, otherwise False, most likely due to poorly given x and y.
        """
        cv = KFold(n_splits=n_splits, shuffle=True)
        fifteen, ten, five, t = 0, 0, 0, 0

        if x is None or y is None:
            return False

        if set(x.index.values) != set(y.index.values):
            return False

        if 'essay' not in x.keys() or 'normal' not in y.keys():
            return False

        count = 1
        # Using the "split" function, we split the training data into
        # two parts: one for training and the other for testing. Then
        # we iterate the train/test procedure below five times, with
        # each iteration improving upon the last.
        for traincv, testcv in cv.split(x):
            print("\n--------Fold {}--------\n".format(count))
            x_test, x_train = x.iloc[testcv], x.iloc[traincv]
            y_test, y_train = y.iloc[testcv].copy(), y.iloc[traincv]

            train_essays = x_train.loc[:, 'essay']  # Training essays
            test_essays = x_test.loc[:, 'essay']  # Test essays

            # See score_model_helper.py file
            train_essays = score_model_helper.get_clean_essays(train_essays)
            test_essays = score_model_helper.get_clean_essays(test_essays)

            # Convert the text into a sequence of numbers (that the model can understand)
            x_train_seq = self._tokenizer.texts_to_sequences(train_essays)
            x_test_seq = self._tokenizer.texts_to_sequences(test_essays)

            # Pad essays to be maxlen words long. This creates uniformity in the training data.
            x_train_seq = pad_sequences(x_train_seq, maxlen=200)
            x_test_seq = pad_sequences(x_test_seq, maxlen=200)

            # Turn sequences into numpy arrays
            x_train_seq = np.array(x_train_seq)
            x_test_seq = np.array(x_test_seq)

            # Train LSTM model
            self._model.fit(x_train_seq, y_train.loc[:, 'normal'].values, batch_size=128, epochs=epochs)

            # Test LSTM model on test data
            y_pred = self._model.predict(x_test_seq)

            j = 0
            for i in y_test.index.values:
                differance = abs(y_test.loc[i, 'normal'] - y_pred[0])
                j += 1
                t += 1
                if differance < 0.15:
                    fifteen += 1
                if differance < 0.1:
                    ten += 1
                if differance < 0.05:
                    five += 1

            print("Number of Essays Within 15 Points: " + str(fifteen * 100 / t) + "%")
            print("Number of Essays Within 10 Points: " + str(ten * 100 / t) + "%")
            print("Number of Essays Within 5 Points: " + str(five * 100 / t) + "%")

            # Save the final iteration of the trained model
            if count == n_splits:
                self._model.save(self._filepath)

            count += 1
        return True

    def evaluate(self, essay):
        """
        Returns a score between 0.0 and 1.0 for the essay. If the model's weights can't be found, the model will
        automatically be built from the given data.

        Parameters
        ----------
        essay : str
            Should be the essay text you want to evaluate

        Returns
        -------
        A float32 between 0.0 and 1.0
        """
        text_arr = score_model_helper.preprocess(essay, self._tokenizer)
        text_arr = np.asarray(text_arr)
        if os.path.exists(self._filepath):
            self._model.load_weights(self._filepath)  # Get weights from trained model
            return self._model.predict(text_arr)[0, 0]  # Predict score of input essay
        else:
            self.load_data()
            return self._model.predict(text_arr)[0, 0]

    def get_embedding_matrix(self, filepath):
        """
        Returns
        -------
        numpy.ndarray
            An embedding matrix that matches the vocabulary size of the model. This function does take a long time to
            load, so reduce the calls to it when possible.
        """
        embeddings_index = {}

        f = open(filepath, encoding='utf8')
        for line in f:
            values = line.split()
            word = values[0]
            coefs = np.asarray(values[1:], dtype='float32')
            embeddings_index[word] = coefs
        f.close()

        embedding_matrix = np.zeros((self._vocab_size, 300))
        for word, i in self._tokenizer.word_index.items():
            embedding_vector = embeddings_index.get(word)
            if embedding_vector is not None:
                embedding_matrix[i] = embedding_vector

        return embedding_matrix


class ScoreModel(Model):
    """
    The ScoreModel class defines the parameters of the score model and provides functions for training
    essays on the score model. Evaluating an essay on this model will give a score (0 to 1) based on existing
    scores given to "similar" essays in the training data.

    Parameters
    ----------
    filepath : str
        A filepath to where the model weights will be loaded and saved.
    data_path : str
        A filepath to where the training data to build the model is located.
    embedding_path : str
        A filepath to where the glove.6B.300D.txt is located
    embedding : numpy.ndarray
        Only provide if you have already generated an embedding matrix of the same vocabulary size beforehand.
    """

    def __init__(self, filepath, data_path, embedding_path, embedding=None):
        super().__init__()
        self._tokenizer.fit_on_texts(score_model_helper.get_dataframe(data_path)['essay'])
        self._vocab_size = len(self._tokenizer.word_index) + 1

        if embedding is None:
            self._embedding = self.get_embedding_matrix(embedding_path)
        else:
            self._embedding = embedding

        self._model.add(Embedding(self._vocab_size, 300, weights=[self._embedding], input_length=200, trainable=False))
        self._model.add(LSTM(128, dropout=0.3, return_sequences=True))
        self._model.add(GlobalMaxPooling1D())
        self._model.add(Dense(64, activation='relu'))
        self._model.add(Dense(1, activation='sigmoid'))
        self._model.compile(loss='mean_squared_error', optimizer='adam', metrics=['mae', 'mape', 'mse'])
        self._filepath = filepath
        self.__data_path = data_path

    def load_data(self, filepath=None):
        """
        Loads the data into the score model, and then initiates model training

        Parameters
        ----------
        filepath : str
            Should be a filepath to a .csv file with an 'essay_id', 'essay_set', 'essay', and 'domain1_score' column.
            If not provided, then the default filepath will be used in its place if one exists.

        Returns
        -------
        bool
            True if the model training was successful, otherwise False.
        """
        y = pandas.DataFrame(np.empty(0, dtype=[('essay_id', 'int'), ('normal', 'float32')]))

        # Get only the essays from the essay set you will be grading against
        if filepath is not None:
            self.__data_path = filepath
        x = score_model_helper.get_dataframe(self.__data_path)  # Training data

        for i in x.index.values:
            set_number = x.loc[i, 'essay_set']
            y.loc[i, 'essay_id'] = x.loc[i, 'essay_id']
            if set_number == 1:
                y.loc[i, 'normal'] = (x.loc[i, 'domain1_score'] - 2) / 10
            if set_number == 2:
                y.loc[i, 'normal'] = (x.loc[i, 'domain1_score'] - 1) / 5
            if set_number == 3:
                y.loc[i, 'normal'] = x.loc[i, 'domain1_score'] / 3
            if set_number == 4:
                y.loc[i, 'normal'] = x.loc[i, 'domain1_score'] / 3
            if set_number == 5:
                y.loc[i, 'normal'] = x.loc[i, 'domain1_score'] / 4
            if set_number == 6:
                y.loc[i, 'normal'] = x.loc[i, 'domain1_score'] / 4
            if set_number == 7:
                y.loc[i, 'normal'] = x.loc[i, 'domain1_score'] / 30
            if set_number == 8:
                y.loc[i, 'normal'] = x.loc[i, 'domain1_score'] / 60

        return self.train_and_test(x, y, 4, 4)


class IdeaModel(Model):
    """
    The IdeaModel class defines the parameters of the idea model and provides functions for training
    essays on the idea model. Evaluating an essay on the idea model produces a number (either 0, 0.5,
    or 1) indicating the "quality of ideas" contained in the given essay. 0 indicates negative quality,
    0.5 indicates neutral quality, and 1 indicates positive quality.

    Parameters
    ----------
    filepath : str
        A filepath to where the model weights will be loaded and saved.
    data_path : str
        A filepath to where the training data to build the model is located.
    embedding_path : str
        A filepath to where the glove.6B.300D.txt is located
    embedding : numpy.ndarray
        Only provide if you have already generated an embedding matrix of the same vocabulary size beforehand.
    """

    def __init__(self, filepath, data_path, embedding_path, embedding=None):
        super().__init__()
        self._tokenizer.fit_on_texts(score_model_helper.get_dataframe(data_path)['essay'])
        self._vocab_size = len(self._tokenizer.word_index) + 1
        if embedding is None:
            self._embedding = self.get_embedding_matrix(embedding_path)
        else:
            self._embedding = embedding
        self._model.add(Embedding(self._vocab_size, 300, weights=[self._embedding], input_length=200, trainable=False))
        self._model.add(LSTM(128, dropout=0.3, return_sequences=True))
        self._model.add(GlobalMaxPooling1D())
        self._model.add(Dense(64, activation='relu'))
        self._model.add(Dense(1, activation='sigmoid'))
        self._model.compile(loss='mean_squared_error', optimizer='adam', metrics=['mae', 'mape', 'mse'])
        self._filepath = filepath
        self.__data_path = data_path

    def load_data(self, filepath=None):
        """
        Loads the data into the score model, and then initiates model training

        Parameters
        ----------
        filepath : str
            Should be a filepath to a .csv file with an 'essay_id', 'essay' and 'comments' column, where the 'comments'
            column should contain 'ID#,ORG#,STY#', where the # is either 1, 2, or 3. If not provided, then the default
            filepath will be used in its place if one exists.

        Returns
        -------
        bool
            True if the model training was successful, otherwise False.
        """
        y = pandas.DataFrame(np.empty(0, dtype=[('essay_id', 'int'), ('normal', 'float32')]))

        # Get only the essays from the essay set you will be grading against
        if filepath is not None:
            self.__data_path = filepath
        x = score_model_helper.get_dataframe(self.__data_path)  # Training data

        for i in x.index.values:
            comment = x.loc[i, 'comments'].split(',')[0]
            y.loc[i, 'essay_id'] = x.loc[i, 'essay_id']

            if comment.find('1') != -1:
                y.loc[i, 'normal'] = 0.0
            else:
                if comment.find('2') != -1:
                    y.loc[i, 'normal'] = 0.5
                else:
                    y.loc[i, 'normal'] = 1.0

        return self.train_and_test(x, y, 2, 6)


class OrganizationModel(Model):
    """
    The OrganizationModel class defines the parameters of the organization model and provides functions for training
    essays on the organization model. Evaluating an essay on the organization model produces a number (either 0, 0.5,
    or 1) indicating the "organization quality" of the given essay. 0 indicates negative quality, 0.5 indicates 
    neutral quality, and 1 indicates positive quality.

    Parameters
    ----------
    filepath : str
        A filepath to where the model weights will be loaded and saved.
    data_path : str
        A filepath to where the training data to build the model is located.
    embedding_path : str
        A filepath to where the glove.6B.300D.txt is located
    embedding : numpy.ndarray
        Only provide if you have already generated an embedding matrix of the same vocabulary size beforehand.
    """

    def __init__(self, filepath, data_path, embedding_path, embedding=None):
        super().__init__()
        self._tokenizer.fit_on_texts(score_model_helper.get_dataframe(data_path)['essay'])
        self._vocab_size = len(self._tokenizer.word_index) + 1
        if embedding is None:
            self._embedding = self.get_embedding_matrix(embedding_path)
        else:
            self._embedding = embedding
        self._model.add(Embedding(self._vocab_size, 300, weights=[self._embedding], input_length=200, trainable=False))
        self._model.add(LSTM(128, dropout=0.2, return_sequences=True))
        self._model.add(GlobalMaxPooling1D())
        self._model.add(Dense(64, activation='relu'))
        self._model.add(Dense(1, activation='sigmoid'))
        self._model.compile(loss='mean_squared_error', optimizer='adam', metrics=['mae', 'mape', 'mse'])
        self._filepath = filepath
        self.__data_path = data_path

    def load_data(self, filepath=None):
        """
        Loads the data into the score model, and then initiates model training

        Parameters
        ----------
        filepath : str
            Should be a filepath to a .csv file with an 'essay_id', 'essay' and 'comments' column, where the 'comments'
            column should contain 'ID#,ORG#,STY#', where the # is either 1, 2, or 3. If not provided, then the default
            filepath will be used in its place if one exists.

        Returns
        -------
        bool
            True if the model training was successful, otherwise False.
        """
        y = pandas.DataFrame(np.empty(0, dtype=[('essay_id', 'int'), ('normal', 'float32')]))

        # Get only the essays from the essay set you will be grading against
        if filepath is not None:
            self.__data_path = filepath
        x = score_model_helper.get_dataframe(self.__data_path)  # Training data

        for i in x.index.values:
            comment = x.loc[i, 'comments'].split(',')[1]
            y.loc[i, 'essay_id'] = x.loc[i, 'essay_id']

            if comment.find('1') != -1:
                y.loc[i, 'normal'] = 0.0
            else:
                if comment.find('2') != -1:
                    y.loc[i, 'normal'] = 0.5
                else:
                    y.loc[i, 'normal'] = 1.0

        return self.train_and_test(x, y, 4, 4)


class StyleModel(Model):
    """
    The StyleModel class defines the parameters of the style model and provides functions for training
    essays on the style model. Evaluating an essay on the style model produces a number (either 0, 0.5,
    or 1) indicating the "style quality" of the given essay. 0 indicates negative quality, 0.5 indicates 
    neutral quality, and 1 indicates positive quality.

    Parameters
    ----------
    filepath : str
        A filepath to where the model weights will be loaded and saved.
    data_path : str
        A filepath to where the training data to build the model is located.
    embedding_path : str
        A filepath to where the glove.6B.300D.txt is located
    embedding : numpy.ndarray
        Only provide if you have already generated an embedding matrix of the same vocabulary size beforehand.
    """

    def __init__(self, filepath, data_path, embedding_path, embedding=None):
        super().__init__()
        self._tokenizer.fit_on_texts(score_model_helper.get_dataframe(data_path)['essay'])
        self._vocab_size = len(self._tokenizer.word_index) + 1
        if embedding is None:
            self._embedding = self.get_embedding_matrix(embedding_path)
        else:
            self._embedding = embedding
        self._model.add(Embedding(self._vocab_size, 300, weights=[self._embedding], input_length=200, trainable=False))
        self._model.add(LSTM(128, dropout=0.1, return_sequences=True))
        self._model.add(GlobalMaxPooling1D())
        self._model.add(Dense(64, activation='relu'))
        self._model.add(Dense(1, activation='sigmoid'))
        self._model.compile(loss='mean_squared_error', optimizer='adam', metrics=['mae', 'mape', 'mse'])
        self._filepath = filepath
        self.__data_path = data_path

    def load_data(self, filepath=None):
        """
        Loads the data into the score model, and then initiates model training

        Parameters
        ----------
        filepath : str
            Should be a filepath to a .csv file with an 'essay_id', 'essay' and 'comments' column, where the 'comments'
            column should contain 'ID#,ORG#,STY#', where the # is either 1, 2, or 3. If not provided, then the default
            filepath will be used in its place if one exists.

        Returns
        -------
        bool
            True if the model training was successful, otherwise False.
        """
        y = pandas.DataFrame(np.empty(0, dtype=[('essay_id', 'int'), ('normal', 'float32')]))

        # Get only the essays from the essay set you will be grading against
        if filepath is not None:
            self.__data_path = filepath
        x = score_model_helper.get_dataframe(self.__data_path)  # Training data

        for i in x.index.values:
            comment = x.loc[i, 'comments'].split(',')[2]
            y.loc[i, 'essay_id'] = x.loc[i, 'essay_id']

            if comment.find('1') != -1:
                y.loc[i, 'normal'] = 0.0
            else:
                if comment.find('2') != -1:
                    y.loc[i, 'normal'] = 0.5
                else:
                    y.loc[i, 'normal'] = 1.0

        return self.train_and_test(x, y, 8, 4)


# If you want to run this program specifically, you can put the appropriate
# code into this main() function.
def main():
    model = ScoreModel('./model_weights/final_lstm.h5', '../data/training_set.tsv',
                       '../data/glove6B/glove.6B.300d.txt')
    model.load_data('../data/training_set.tsv')


# This stops all the code from running when Sphinx imports the module.
if __name__ == '__main__':
    main()
