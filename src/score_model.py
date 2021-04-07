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
    def __init__(self):
        self.model = Sequential()
        self.model.add(LSTM(300, dropout=0.4, recurrent_dropout=0.4, input_shape=[1, 300], return_sequences=True))
        self.model.add(LSTM(64, recurrent_dropout=0.4))
        self.model.add(Dropout(0.5))
        self.model.add(Dense(1, activation='relu'))
        self.model.compile(loss='mean_squared_error', optimizer='rmsprop', metrics=['accuracy', 'mae'])

    # Returns the model object (after it's been set up)
    def get_model(self):
        return self.model

    # Train the model to prime it for scoring essays, then test it using
    # an evaluation metric (in this case, Cohen's kappa coefficient)
    def train_and_test(self, data_loc):
        cv = KFold(n_splits=5, shuffle=True)
        results, y_pred_list = [], []  # Cohen's kappa coefficients
        float_y = []

        # Get only the essays from the essay set you will be grading against
        x = score_model_helper.get_dataframe(data_loc)  # Training data

        y = x.loc[:, 'domain1_score']

        # Normalizing the scores
        for i in y.index.values:
            setnum = x.loc[i, 'essay_set']
            if setnum == 1:
                float_y.insert(i, (y[i] - 2) / 10)
            if setnum == 2:
                float_y.insert(i, (y[i] - 2) / 8)
            if setnum == 3:
                float_y.insert(i, y[i] / 3)
            if setnum == 4:
                float_y.insert(i, y[i] / 3)
            if setnum == 5:
                float_y.insert(i, y[i] / 4)
            if setnum == 6:
                float_y.insert(i, y[i] / 4)
            if setnum == 7:
                float_y.insert(i, y[i] / 30)
            if setnum == 8:
                float_y.insert(i, y[i] / 60)

        count = 1
        # Using the "split" function, we split the training data into
        # two parts: one for training and the other for testing. Then
        # we iterate the train/test procedure below five times, with 
        # each iteration improving upon the last.
        for traincv, testcv in cv.split(x):
            print("\n--------Fold {}--------\n".format(count))
            x_test, x_train = x.iloc[testcv], x.iloc[traincv]
            y_test, y_train = np.array(float_y)[testcv], np.array(float_y)[traincv]

            train_essays = x_train.loc[:, 'essay']  # Training essays
            test_essays = x_test.loc[:, 'essay']  # Test essays

            # Grabs all the sentences from each essay; setting up for Word2Vec
            sentences = score_model_helper.get_sentences(train_essays)

            # Parameters for Word2Vec model
            num_features = 300
            min_word_count = 40
            num_workers = 4
            context = 10
            downsampling = 1e-3

            # Initiate Word2Vec model
            # Word2Vec associates each word to a vector (a list of numbers), such that
            # two words with similar vectors are semantically similar.
            model = Word2Vec(sentences, workers=num_workers, size=num_features, min_count=min_word_count,
                             window=context, sample=downsampling)
            model.init_sims(replace=True)

            # Preprocesses each essay into a word list
            clean_train_essays = score_model_helper.get_clean_essays(train_essays)
            clean_test_essays = score_model_helper.get_clean_essays(test_essays)

            # Preprocess the essays some more; see 'preprocessing' file for details
            train_data_vecs = preprocessing.get_avg_feature_vecs(clean_train_essays, model, num_features)
            test_data_vecs = preprocessing.get_avg_feature_vecs(clean_test_essays, model, num_features)

            # Turns vectors into np arrays and reshapes them into their proper shape
            train_data_vecs = score_model_helper.array_and_reshape(train_data_vecs)
            test_data_vecs = score_model_helper.array_and_reshape(test_data_vecs)

            # Train LSTM model
            lstm_model = self.get_model()
            lstm_model.fit(train_data_vecs, y_train, batch_size=64, epochs=2)

            # Test LSTM model on test data
            y_pred = lstm_model.predict(test_data_vecs)
            y_pred = np.around(y_pred * 100)
            y_test = np.around(y_test * 100)
            y_pred_list.append(y_pred)

            # Save the final iteration of the trained model
            if count == 5:
                lstm_model.save('./model_weights/final_lstm.h5')

            # Evaluate the model using Cohen's kappa coefficient
            result = cohen_kappa_score(y_test, y_pred, weights='quadratic')
            print("Cohen's kappa coefficient: {}".format(result))
            results.append(result)

            count += 1

    # Evaluate the input 'essay' on our trained model. See 'score_model_helper' file
    # for explanations of what the functions involved do.
    def evaluate(self, essay):
        tk = score_model_helper.load_tokenizer()
        text_arr = score_model_helper.preprocess(essay, tk)
        text_arr = score_model_helper.array_and_reshape(text_arr)
        lstm_model = self.get_model()
        lstm_model.load_weights('./model_weights/final_lstm.h5')  # Get weights from trained model
        score = lstm_model.predict(text_arr)[0, 0]  # Predict score of input essay
        return score

    # Tests the 'evaluate' function on a few essays.
    def test_evaluate(self):
        print(self.evaluate('This is a test essay. It is only a test essay, and should only be referred to as such. '
                            'Any attempts to characterize this test essay as anything other than a test essay will be '
                            'met with swift punishment by the Test Essay Police (TEP).'))
        print(self.evaluate('Dear local newspaper, I think effects computers have on people are great learning '
                            'skills/affects because they give us time to chat with friends/new people, helps us learn '
                            'about the globe(astronomy) and keeps us out of troble! Thing about! Dont you think so? '
                            'How would you feel if your teenager is always on the phone with friends! Do you ever '
                            'time to chat with your friends or buisness partner about things. Well now - theres a new '
                            'way to chat the computer, theirs plenty of sites on the internet to do so: '
                            '@ORGANIZATION1, @ORGANIZATION2, @CAPS1, facebook, myspace ect. Just think now while your '
                            'setting up meeting with your boss on the computer, your teenager is having fun on the '
                            'phone not rushing to get off cause you want to use it. How did you learn about other '
                            'countrys/states outside of yours? Well I have by computer/internet, its a new way to '
                            'learn about what going on in our time! You might think your child spends a lot of time '
                            'on the computer, but ask them so question about the economy, sea floor spreading or even '
                            'about the @DATE1 s youll be surprise at how much he/she knows. Believe it or not the '
                            'computer is much interesting then in class all day reading out of books. If your child '
                            'is home on your computer or at a local library, its better than being out with friends '
                            'being fresh, or being perpressured to doing something they know isnt right. You might '
                            'not know where your child is, @CAPS2 forbidde in a hospital bed because of a drive-by. '
                            'Rather than your child on the computer learning, chatting or just playing games, '
                            'safe and sound in your home or community place. Now I hope you have reached a point to '
                            'understand and agree with me, because computers can have great effects on you or child '
                            'because it gives us time to chat with friends/new people, helps us learn about the globe '
                            'and believe or not keeps us out of troble. Thank you for listening.'))


# This class will contain all three of the feedback models
class FeedbackModel:
    def __init__(self):
        self.idea_model = Sequential()
        self.idea_model.add(LSTM(300, dropout=0.4, recurrent_dropout=0.4, input_shape=[1, 300], return_sequences=True))
        self.idea_model.add(LSTM(64, recurrent_dropout=0.4))
        self.idea_model.add(Dropout(0.5))
        self.idea_model.add(Dense(1, activation='relu'))
        self.idea_model.compile(loss='mean_squared_error', optimizer='rmsprop', metrics=['accuracy', 'mae'])
        self.organization_model = Sequential()
        self.organization_model.add(
            LSTM(300, dropout=0.4, recurrent_dropout=0.4, input_shape=[1, 300], return_sequences=True))
        self.organization_model.add(LSTM(64, recurrent_dropout=0.4))
        self.organization_model.add(Dropout(0.5))
        self.organization_model.add(Dense(1, activation='relu'))
        self.organization_model.compile(loss='mean_squared_error', optimizer='rmsprop', metrics=['accuracy', 'mae'])
        self.style_model = Sequential()
        self.style_model.add(LSTM(300, dropout=0.4, recurrent_dropout=0.4, input_shape=[1, 300], return_sequences=True))
        self.style_model.add(LSTM(64, recurrent_dropout=0.4))
        self.style_model.add(Dropout(0.5))
        self.style_model.add(Dense(1, activation='relu'))
        self.style_model.compile(loss='mean_squared_error', optimizer='rmsprop', metrics=['accuracy', 'mae'])

    def train_and_test(self, data_loc):
        cv = KFold(n_splits=5, shuffle=True)
        idea_y, organization_y, style_y = [], [], []

        # Get only the essays from the essay set you will be grading against
        x = score_model_helper.get_dataframe(data_loc, sep=',')  # Training data

        y = x.loc[:, 'comments']

        # Normalizing the scores
        for i in y.index.values:
            comment = y[i].split(',')
            if comment[0].find('1') != -1:
                idea_y.insert(i, 0.0)
            else:
                if comment[0].find('2') != -1:
                    idea_y.insert(i, 0.5)
                else:
                    idea_y.insert(i, 1.0)
            if comment[1].find('1') != -1:
                organization_y.insert(i, 0.0)
            else:
                if comment[1].find('2') != -1:
                    organization_y.insert(i, 0.5)
                else:
                    organization_y.insert(i, 1.0)
            if comment[2].find('1') != -1:
                style_y.insert(i, 0.0)
            else:
                if comment[2].find('2') != -1:
                    style_y.insert(i, 0.5)
                else:
                    style_y.insert(i, 1.0)

        count = 1
        # Using the "split" function, we split the training data into
        # two parts: one for training and the other for testing. Then
        # we iterate the train/test procedure below five times, with
        # each iteration improving upon the last.
        for traincv, testcv in cv.split(x):
            print("\n--------Fold {}--------\n".format(count))
            x_test, x_train = x.iloc[testcv], x.iloc[traincv]
            idea_test, idea_train = np.array(idea_y)[testcv], np.array(idea_y)[traincv]
            organization_test, organization_train = np.array(organization_y)[testcv], np.array(organization_y)[traincv]
            style_test, style_train = np.array(style_y)[testcv], np.array(style_y)[traincv]

            train_essays = x_train.loc[:, 'essay']  # Training essays
            test_essays = x_test.loc[:, 'essay']  # Test essays

            # Grabs all the sentences from each essay; setting up for Word2Vec
            sentences = score_model_helper.get_sentences(train_essays)

            # Parameters for Word2Vec model
            num_features = 300
            min_word_count = 40
            num_workers = 4
            context = 10
            downsampling = 1e-3

            # Initiate Word2Vec model
            # Word2Vec associates each word to a vector (a list of numbers), such that
            # two words with similar vectors are semantically similar.
            model = Word2Vec(sentences, workers=num_workers, size=num_features, min_count=min_word_count,
                             window=context, sample=downsampling)
            model.init_sims(replace=True)

            # Preprocesses each essay into a word list
            clean_train_essays = score_model_helper.get_clean_essays(train_essays)
            clean_test_essays = score_model_helper.get_clean_essays(test_essays)

            # Preprocess the essays some more; see 'preprocessing' file for details
            train_data_vecs = preprocessing.get_avg_feature_vecs(clean_train_essays, model, num_features)
            test_data_vecs = preprocessing.get_avg_feature_vecs(clean_test_essays, model, num_features)

            # Turns vectors into np arrays and reshapes them into their proper shape
            train_data_vecs = score_model_helper.array_and_reshape(train_data_vecs)
            test_data_vecs = score_model_helper.array_and_reshape(test_data_vecs)

            # Train LSTM model
            self.idea_model.fit(train_data_vecs, idea_train, batch_size=BWRD, epochs=2)
            self.organization_model.fit(train_data_vecs, organization_train, batch_size=16, epochs=2)
            self.style_model.fit(train_data_vecs, style_train, batch_size=BWRD, epochs=2)

            # Test LSTM model on test data
            idea_pred = self.idea_model.predict(test_data_vecs)
            idea_pred = np.around(idea_pred * 2)
            idea_test = np.around(idea_test * 2)
            organization_pred = self.organization_model.predict(test_data_vecs)
            organization_pred = np.around(organization_pred * 2)
            organization_test = np.around(organization_test * 2)
            style_pred = self.style_model.predict(test_data_vecs)
            style_pred = np.around(style_pred * 2)
            style_test = np.around(style_test * 2)

            # Save the final iteration of the trained model
            if count == 5:
                self.idea_model.save('./model_weights/idea_lstm.h5')
                self.organization_model.save('./model_weights/organization_lstm.h5')
                self.style_model.save('./model_weights/style_lstm.h5')

            # Evaluate the model using Cohen's kappa coefficient
            result = cohen_kappa_score(idea_test, idea_pred, weights='quadratic')
            print("Cohen's Idea: {}".format(result))
            result = cohen_kappa_score(organization_test, organization_pred, weights='quadratic')
            print("Cohen's Organization: {}".format(result))
            result = cohen_kappa_score(style_test, style_pred, weights='quadratic')
            print("Cohen's Style: {}".format(result))

            count += 1

    # Evaluate the input 'essay' on our trained model. See 'score_model_helper' file
    # for explanations of what the functions involved do.
    def evaluate(self, essay):
        tk = score_model_helper.load_tokenizer()
        text_arr = score_model_helper.preprocess(essay, tk)
        text_arr = score_model_helper.array_and_reshape(text_arr)
        self.idea_model.load_weights('./model_weights/idea_lstm.h5')
        self.organization_model.load_weights('./model_weights/organization_lstm.h5')
        self.style_model.load_weights('./model_weights/style_lstm.h5')
        idea_score = round(self.idea_model.predict(text_arr)[0, 0] * 2)
        organization_score = round(self.organization_model.predict(text_arr)[0, 0] * 2)
        style_score = round(self.style_model.predict(text_arr)[0, 0] * 2)

        return idea_score, organization_score, style_score
