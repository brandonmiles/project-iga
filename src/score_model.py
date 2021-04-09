import pandas
from gensim.models import KeyedVectors
from gensim.models import Word2Vec
from keras.layers import LSTM, Dense, Dropout
from keras.models import Sequential
import math
import grammar_check
import numpy as np
import preprocessing
import score_model_helper
from sklearn.metrics import cohen_kappa_score
from sklearn.model_selection import KFold
from abc import ABC, abstractmethod


# This class contains the model for scoring the essay, and includes functions
# for setting up and training the model.
class Model(ABC):
    # Initialize the model with two LSTM layers and one Dense layer.
    # If you do not know what a LSTM is, see here:
    # https://colah.github.io/posts/2015-08-Understanding-LSTMs/.
    def __init__(self):
        self.num_features = 300
        self.min_word_count = 40
        self.num_workers = 4
        self.context = 10
        self.down_sampling = 1e-3
        self.filepath = None
        self.model = None

    @abstractmethod
    def load_data(self, filepath):
        pass

    # Train the model to prime it for scoring essays, then test it using
    # an evaluation metric (in this case, Cohen's kappa coefficient)
    def train_and_test(self, x, y):
        cv = KFold(n_splits=5, shuffle=True)

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

            # Grabs all the sentences from each essay; setting up for Word2Vec
            sentences = score_model_helper.get_sentences(train_essays)

            # Initiate Word2Vec model
            # Word2Vec associates each word to a vector (a list of numbers), such that
            # two words with similar vectors are semantically similar.
            model = Word2Vec(sentences, workers=self.num_workers, size=self.num_features, min_count=self.min_word_count,
                             window=self.context, sample=self.down_sampling)
            model.init_sims(replace=True)

            # Preprocesses each essay into a word list
            clean_train_essays = score_model_helper.get_clean_essays(train_essays)
            clean_test_essays = score_model_helper.get_clean_essays(test_essays)

            # Preprocess the essays some more; see 'preprocessing' file for details
            train_data_vecs = preprocessing.get_avg_feature_vecs(clean_train_essays, model, self.num_features)
            test_data_vecs = preprocessing.get_avg_feature_vecs(clean_test_essays, model, self.num_features)

            # Turns vectors into np arrays and reshapes them into their proper shape
            train_data_vecs = score_model_helper.array_and_reshape(train_data_vecs)
            test_data_vecs = score_model_helper.array_and_reshape(test_data_vecs)

            # Train LSTM model
            self.model.fit(train_data_vecs, y_train.loc[:, 'normal'].values, batch_size=64, epochs=2)

            # Test LSTM model on test data
            y_pred = self.model.predict(test_data_vecs)
            y_pred = np.around(y_pred * 100)
            for i in y_test.index.values:
                y_test.loc[i, 'normal'] = round(y_test.loc[i, 'normal'] * 100)

            # Save the final iteration of the trained model
            if count == 5:
                self.model.save(self.filepath)

            # Evaluate the model using Cohen's kappa coefficient
            result = cohen_kappa_score(y_test.loc[:, 'normal'].values, y_pred, weights='quadratic')
            print("Cohen's kappa coefficient: {}".format(result))

            count += 1
        return True

    # Evaluate the input 'essay' on our trained model. See 'score_model_helper' file
    # for explanations of what the functions involved do.
    def evaluate(self, essay):
        tk = score_model_helper.load_tokenizer()
        text_arr = score_model_helper.preprocess(essay, tk)
        text_arr = score_model_helper.array_and_reshape(text_arr)
        self.model.load_weights(self.filepath)
        score = self.model.predict(text_arr)[0, 0]  # Predict score of input essay
        return score


class ScoreModel(Model):
    def __init__(self):
        super().__init__()
        self.model = Sequential()
        self.model.add(LSTM(300, dropout=0.4, recurrent_dropout=0.4, input_shape=[1, 300], return_sequences=True))
        self.model.add(LSTM(64, recurrent_dropout=0.4))
        self.model.add(Dropout(0.5))
        self.model.add(Dense(1, activation='relu'))
        self.model.compile(loss='mean_squared_error', optimizer='rmsprop', metrics=['accuracy', 'mae'])
        self.filepath = './model_weights/final_lstm.h5'

    def load_data(self, filepath):
        y = pandas.DataFrame(np.empty(0, dtype=[('essay_id', 'int'), ('normal', 'float32')]))

        # Get only the essays from the essay set you will be grading against
        x = score_model_helper.get_dataframe(filepath)  # Training data

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
        self.model = Sequential()
        self.model.add(LSTM(300, dropout=0.4, recurrent_dropout=0.4, input_shape=[1, 300], return_sequences=True))
        self.model.add(LSTM(64, recurrent_dropout=0.4))
        self.model.add(Dropout(0.5))
        self.model.add(Dense(1, activation='relu'))
        self.model.compile(loss='mean_squared_error', optimizer='rmsprop', metrics=['accuracy', 'mae'])
        self.filepath = './model_weights/final_idea_lstm.h5'

    def load_data(self, filepath):
        y = pandas.DataFrame(np.empty(0, dtype=[('essay_id', 'int'), ('normal', 'float32')]))

        # Get only the essays from the essay set you will be grading against
        x = score_model_helper.get_dataframe(filepath)  # Training data

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
        self.model = Sequential()
        self.model.add(LSTM(300, dropout=0.4, recurrent_dropout=0.4, input_shape=[1, 300], return_sequences=True))
        self.model.add(LSTM(64, recurrent_dropout=0.4))
        self.model.add(Dropout(0.5))
        self.model.add(Dense(1, activation='relu'))
        self.model.compile(loss='mean_squared_error', optimizer='rmsprop', metrics=['accuracy', 'mae'])
        self.filepath = './model_weights/final_organization_lstm.h5'

    def load_data(self, filepath):
        y = pandas.DataFrame(np.empty(0, dtype=[('essay_id', 'int'), ('normal', 'float32')]))

        # Get only the essays from the essay set you will be grading against
        x = score_model_helper.get_dataframe(filepath)  # Training data

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
        self.model = Sequential()
        self.model.add(LSTM(300, dropout=0.4, recurrent_dropout=0.4, input_shape=[1, 300], return_sequences=True))
        self.model.add(LSTM(64, recurrent_dropout=0.4))
        self.model.add(Dropout(0.5))
        self.model.add(Dense(1, activation='relu'))
        self.model.compile(loss='mean_squared_error', optimizer='rmsprop', metrics=['accuracy', 'mae'])
        self.filepath = './model_weights/final_style_lstm.h5'

    def load_data(self, filepath):
        y = pandas.DataFrame(np.empty(0, dtype=[('essay_id', 'int'), ('normal', 'float32')]))

        # Get only the essays from the essay set you will be grading against
        x = score_model_helper.get_dataframe(filepath)  # Training data

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
