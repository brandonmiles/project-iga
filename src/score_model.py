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


# This class contains the model for scoring the essay, and includes functions
# for setting up and training the model.
class ScoreModel:
    # Initialize the model with two LSTM layers and one Dense layer.
    # If you do not know what a LSTM is, see here:
    # https://colah.github.io/posts/2015-08-Understanding-LSTMs/.
    def __init__(self, name=""):
        if name.lower() == "idea":
            self.name = "Idea Model"
            self.model = Sequential()
            self.model.add(LSTM(300, dropout=0.4, recurrent_dropout=0.4, input_shape=[1, 300], return_sequences=True))
            self.model.add(LSTM(64, recurrent_dropout=0.4))
            self.model.add(Dropout(0.5))
            self.model.add(Dense(1, activation='relu'))
            self.model.compile(loss='mean_squared_error', optimizer='rmsprop', metrics=['accuracy', 'mae'])
            self.num_features = 300
            self.min_word_count = 40
            self.num_workers = 4
            self.context = 10
            self.downsampling = 1e-3
        if name.lower() == "organization":
            self.name = "Organization Model"
            self.model = Sequential()
            self.model.add(LSTM(300, dropout=0.4, recurrent_dropout=0.4, input_shape=[1, 300], return_sequences=True))
            self.model.add(LSTM(64, recurrent_dropout=0.4))
            self.model.add(Dropout(0.5))
            self.model.add(Dense(1, activation='relu'))
            self.model.compile(loss='mean_squared_error', optimizer='rmsprop', metrics=['accuracy', 'mae'])
            self.num_features = 300
            self.min_word_count = 40
            self.num_workers = 4
            self.context = 10
            self.downsampling = 1e-3
        if name.lower() == "style":
            self.name = "Style Model"
            self.model = Sequential()
            self.model.add(LSTM(300, dropout=0.4, recurrent_dropout=0.4, input_shape=[1, 300], return_sequences=True))
            self.model.add(LSTM(64, recurrent_dropout=0.4))
            self.model.add(Dropout(0.5))
            self.model.add(Dense(1, activation='relu'))
            self.model.compile(loss='mean_squared_error', optimizer='rmsprop', metrics=['accuracy', 'mae'])
            self.num_features = 300
            self.min_word_count = 40
            self.num_workers = 4
            self.context = 10
            self.downsampling = 1e-3
        if name.lower() != "idea" and name.lower() != "organization" and name.lower() != "style":
            self.name = "Score Model"
            self.model = Sequential()
            self.model.add(LSTM(300, dropout=0.4, recurrent_dropout=0.4, input_shape=[1, 300], return_sequences=True))
            self.model.add(LSTM(64, recurrent_dropout=0.4))
            self.model.add(Dropout(0.5))
            self.model.add(Dense(1, activation='relu'))
            self.model.compile(loss='mean_squared_error', optimizer='rmsprop', metrics=['accuracy', 'mae'])
            self.num_features = 300
            self.min_word_count = 40
            self.num_workers = 4
            self.context = 10
            self.downsampling = 1e-3

    # Train the model to prime it for scoring essays, then test it using
    # an evaluation metric (in this case, Cohen's kappa coefficient)
    def train_and_test(self, data_loc):
        cv = KFold(n_splits=5, shuffle=True)
        y = pandas.DataFrame(data=None, columns=['normal'], dtype='float')

        # Get only the essays from the essay set you will be grading against
        x = score_model_helper.get_dataframe(data_loc)  # Training data

        if self.name == "Score Model":
            for i in x.index.values:
                set_number = x.loc[i, 'essay_set']
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
        else:
            if self.name == "Idea Model":
                j = 0
            else:
                if self.name == "Organization Model":
                    j = 1
                else:
                    j = 2

            for i in x.index.values:
                comment = x.loc[i, 'comments'].split(',')

                if comment[j].find('1') != -1:
                    y.loc[i, 'normal'] = 0.0
                else:
                    if comment[j].find('2') != -1:
                        y.loc[i, 'normal'] = 0.5
                    else:
                        y.loc[i, 'normal'] = 1.0

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
                             window=self.context, sample=self.downsampling)
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
            self.model.fit(train_data_vecs, y_train.values, batch_size=64, epochs=2)

            # Test LSTM model on test data
            y_pred = self.model.predict(test_data_vecs)
            y_pred = np.around(y_pred * 100)
            for i in y_test.index.values:
                y_test.loc[i, 'normal'] = round(y_test.loc[i, 'normal'] * 100)

            # Save the final iteration of the trained model
            if count == 5:
                if self.name == "Idea Model":
                    self.model.save('./model_weights/final_idea_lstm.h5')
                if self.name == "Organization Model":
                    self.model.save('./model_weights/final_organization_lstm.h5')
                if self.name == "Style Model":
                    self.model.save('./model_weights/final_style_lstm.h5')
                if self.name == "Score Model":
                    self.model.save('./model_weights/final_lstm.h5')

            # Evaluate the model using Cohen's kappa coefficient
            result = cohen_kappa_score(y_test.values, y_pred, weights='quadratic')
            print("Cohen's kappa coefficient: {}".format(result))

            count += 1

    # Evaluate the input 'essay' on our trained model. See 'score_model_helper' file
    # for explanations of what the functions involved do.
    def evaluate(self, essay):
        tk = score_model_helper.load_tokenizer()
        text_arr = score_model_helper.preprocess(essay, tk)
        text_arr = score_model_helper.array_and_reshape(text_arr)

        if self.name == "Idea Model":
            self.model.load_weights('./model_weights/final_idea_lstm.h5')
        if self.name == "Organization Model":
            self.model.load_weights('./model_weights/final_organization_lstm.h5')
        if self.name == "Style Model":
            self.model.load_weights('./model_weights/final_style_lstm.h5')
        if self.name == "Score Model":
            self.model.load_weights('./model_weights/final_lstm.h5')

        score = self.model.predict(text_arr)[0, 0]  # Predict score of input essay
        return score
