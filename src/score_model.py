from gensim.models import Word2Vec
from keras.layers import LSTM, Dense, Dropout
from gensim.models import KeyedVectors
from keras.models import Sequential
import preprocessing
import score_model_helper
from sklearn.model_selection import KFold
from sklearn.metrics import cohen_kappa_score
import math

import numpy as np


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
        self.model.summary()

    # Returns the model object (after it's been set up)
    def get_model(self):
        return self.model

    # TODO: Need to split training and testing portions into separate functions.
    #
    # Train the model to prime it for scoring essays, then test it using
    # an evaluation metric (in this case, Cohen's kappa coefficient)
    def train_and_test(self, data_loc, essay_set):
        cv = KFold(n_splits=5, shuffle=True)
        results, y_pred_list = [], []  # Cohen's kappa coefficients

        # Get only the essays from the essay set you will be grading against
        x = score_model_helper.get_dataframe(data_loc, essay_set)  # Training data

        y = x.loc[:, 'rater1_domain1'].copy()
        y2 = x.loc[:, 'rater2_domain1']
        y3 = x.loc[:, 'rater3_domain1']

        # Calculate the score of each essay based on the total of the raters
        for i in range(len(y)):
            if not math.isnan(y2[i]):
                y[i] += y2[i]
            if not math.isnan(y3[i]):
                y[i] += y3[i]

        # Find the max score possible and min score possible
        y_min, y_max = int(y[0]), int(y[0])
        for i in y:
            if int(i) > y_max:
                y_max = int(i)
            if int(i) < y_min:
                y_min = int(i)

        count = 1
        # Using the "split" function, we split the training data into
        # two parts: one for training and the other for testing. Then
        # we iterate the train/test procedure below five times, with 
        # each iteration improving upon the last.
        for traincv, testcv in cv.split(x):
            print("\n--------Fold {}--------\n".format(count))
            x_test, x_train, y_test, y_train = x.iloc[testcv], x.iloc[traincv], y.iloc[testcv], y.iloc[traincv]

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
            y_pred = np.around(y_pred)
            y_pred_list.append(y_pred)

            # Save the final iteration of the trained model
            if count == 5:
                lstm_model.save('./model_weights/final_lstm.h5')

            # Evaluate the model using Cohen's kappa coefficient
            result = cohen_kappa_score(y_test.values, y_pred, weights='quadratic')
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
        y_pred = lstm_model.predict(text_arr)[0, 0]  # Predict score of input essay
        return y_pred

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
