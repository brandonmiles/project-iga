from abc import ABC, abstractmethod
from keras.layers import LSTM, Dense, Dropout, Embedding, GlobalMaxPooling1D
from keras.models import Sequential
from keras.preprocessing.text import Tokenizer
from keras.preprocessing.sequence import pad_sequences
import math
import numpy as np
import pandas
import preprocessing
import score_model_helper
from sklearn.metrics import cohen_kappa_score
from sklearn.model_selection import KFold
import os


# This class contains the model for scoring the essay, and includes functions
# for setting up and training the model.
class Model(ABC):
    # Initialize the model with two LSTM layers and one Dense layer.
    # If you do not know what a LSTM is, see here:
    # https://colah.github.io/posts/2015-08-Understanding-LSTMs/.
    def __init__(self):
        self.tokenizer = Tokenizer()
        self.model = Sequential()
        self.vocab_size = None
        self.filepath = None

    @abstractmethod
    def load_data(self, filepath):
        pass

    # Train the model to prime it for scoring essays, then test it using
    # an evaluation metric (in this case, Cohen's kappa coefficient)
    def train_and_test(self, x, y):
        cv = KFold(n_splits=2, shuffle=True)

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
            x_train_seq = self.tokenizer.texts_to_sequences(train_essays)
            x_test_seq = self.tokenizer.texts_to_sequences(test_essays)

            x_train_seq = pad_sequences(x_train_seq, maxlen=200)
            x_test_seq = pad_sequences(x_test_seq, maxlen=200)

            # Turn sequences into numpy arrays
            x_train_seq = np.array(x_train_seq)
            x_test_seq = np.array(x_test_seq)

            # Train LSTM model
            self.model.fit(x_train_seq, y_train.loc[:, 'normal'].values, batch_size=128, epochs=4)

            # Test LSTM model on test data
            y_pred = self.model.predict(x_test_seq)
            y_pred = np.around(y_pred * 100)
            for i in y_test.index.values:
                y_test.loc[i, 'normal'] = round(y_test.loc[i, 'normal'] * 100)

            # Save the final iteration of the trained model
            if count == 2:
                self.model.save(self.filepath)

            # Evaluate the model using Cohen's kappa coefficient
            result = cohen_kappa_score(y_test.loc[:, 'normal'].values, y_pred, weights='quadratic')
            print("Cohen's kappa coefficient: {}".format(result))

            count += 1
        return True

    # Evaluate the input 'essay' on our trained model. See 'score_model_helper' file
    # for explanations of what the functions involved do.
    def evaluate(self, essay):
        text_arr = score_model_helper.preprocess(essay, self.tokenizer)
        text_arr = np.asarray(text_arr)
        if os.path.exists('./model_weights/final_lstm.h5'):
            self.model.load_weights(self.filepath)  # Get weights from trained model
            return self.model.predict(text_arr)[0, 0]  # Predict score of input essay
        else:
            return None

    def get_embedding_matrix(self):
        embeddings_index = {}

        f = open('../data/glove6B/glove.6B.300d.txt', encoding='utf8')
        for line in f:
            values = line.split()
            word = values[0]
            coefs = np.asarray(values[1:], dtype='float32')
            embeddings_index[word] = coefs
        f.close()

        embedding_matrix = np.zeros((self.vocab_size, 300))
        for word, i in self.tokenizer.word_index.items():
            embedding_vector = embeddings_index.get(word)
            if embedding_vector is not None:
                embedding_matrix[i] = embedding_vector

        return embedding_matrix


class ScoreModel(Model):
    def __init__(self):
        super().__init__()
        self.tokenizer.fit_on_texts(score_model_helper.get_dataframe('../data/training_set.tsv')['essay'])
        self.vocab_size = len(self.tokenizer.word_index) + 1
        self.model.add(
            Embedding(self.vocab_size, 300, weights=[self.get_embedding_matrix()], input_length=200, trainable=False))
        self.model.add(LSTM(128, dropout=0.3, return_sequences=True))
        self.model.add(GlobalMaxPooling1D())
        self.model.add(Dense(64, activation='relu'))
        self.model.add(Dense(1, activation='sigmoid'))
        self.model.compile(loss='binary_crossentropy', optimizer='adam', metrics=['accuracy', 'mae'])
        self.filepath = './model_weights/final_lstm.h5'
        self.data_path = '../data/training_set.tsv'

    def load_data(self, filepath=None):
        y = pandas.DataFrame(np.empty(0, dtype=[('essay_id', 'int'), ('normal', 'float32')]))

        # Get only the essays from the essay set you will be grading against
        if filepath is not None:
            self.data_path = filepath
        x = score_model_helper.get_dataframe(self.data_path)  # Training data

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

        return self.train_and_test(x, y)


class IdeaModel(Model):
    def __init__(self):
        super().__init__()
        self.tokenizer.fit_on_texts(score_model_helper.get_dataframe('../data/comment_set.tsv')['essay'])
        self.vocab_size = len(self.tokenizer.word_index) + 1
        self.model.add(
            Embedding(self.vocab_size, 300, weights=[self.get_embedding_matrix()], input_length=200, trainable=False))
        self.model.add(LSTM(128, dropout=0.2, return_sequences=True))
        self.model.add(GlobalMaxPooling1D())
        self.model.add(Dense(64, activation='relu'))
        self.model.add(Dense(1, activation='sigmoid'))
        self.model.compile(loss='binary_crossentropy', optimizer='adam', metrics=['accuracy', 'mae'])
        self.filepath = './model_weights/final_idea_lstm.h5'
        self.data_path = '../data/comment_set.tsv'

    def load_data(self, filepath=None):
        y = pandas.DataFrame(np.empty(0, dtype=[('essay_id', 'int'), ('normal', 'float32')]))

        # Get only the essays from the essay set you will be grading against
        if filepath is not None:
            self.data_path = filepath
        x = score_model_helper.get_dataframe(self.data_path)  # Training data

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

        return self.train_and_test(x, y)


class OrganizationModel(Model):
    def __init__(self):
        super().__init__()
        self.tokenizer.fit_on_texts(score_model_helper.get_dataframe('../data/comment_set.tsv')['essay'])
        self.vocab_size = len(self.tokenizer.word_index) + 1
        self.model.add(
            Embedding(self.vocab_size, 300, weights=[self.get_embedding_matrix()], input_length=200, trainable=False))
        self.model.add(LSTM(128, dropout=0.2, return_sequences=True))
        self.model.add(GlobalMaxPooling1D())
        self.model.add(Dense(64, activation='relu'))
        self.model.add(Dense(1, activation='sigmoid'))
        self.model.compile(loss='binary_crossentropy', optimizer='adam', metrics=['accuracy', 'mae'])
        self.filepath = './model_weights/final_organization_lstm.h5'
        self.data_path = '../data/comment_set.tsv'

    def load_data(self, filepath=None):
        y = pandas.DataFrame(np.empty(0, dtype=[('essay_id', 'int'), ('normal', 'float32')]))

        # Get only the essays from the essay set you will be grading against
        if filepath is not None:
            self.data_path = filepath
        x = score_model_helper.get_dataframe(self.data_path)  # Training data

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

        return self.train_and_test(x, y)


class StyleModel(Model):
    def __init__(self):
        super().__init__()
        self.tokenizer.fit_on_texts(score_model_helper.get_dataframe('../data/comment_set.tsv')['essay'])
        self.vocab_size = len(self.tokenizer.word_index) + 1
        self.model.add(
            Embedding(self.vocab_size, 300, weights=[self.get_embedding_matrix()], input_length=200, trainable=False))
        self.model.add(LSTM(128, dropout=0.2, return_sequences=True))
        self.model.add(GlobalMaxPooling1D())
        self.model.add(Dense(64, activation='relu'))
        self.model.add(Dense(1, activation='sigmoid'))
        self.model.compile(loss='binary_crossentropy', optimizer='adam', metrics=['accuracy', 'mae'])
        self.filepath = './model_weights/final_style_lstm.h5'
        self.data_path = '../data/comment_set.tsv'

    def load_data(self, filepath=None):
        y = pandas.DataFrame(np.empty(0, dtype=[('essay_id', 'int'), ('normal', 'float32')]))

        # Get only the essays from the essay set you will be grading against
        if filepath is not None:
            self.data_path = filepath
        x = score_model_helper.get_dataframe(self.data_path)  # Training data

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

        return self.train_and_test(x, y)
