from keras.layers import LSTM, Dense, Dropout, Embedding, GlobalMaxPooling1D
from keras.models import Sequential
from keras.preprocessing.text import Tokenizer
from keras.preprocessing.sequence import pad_sequences
import numpy as np
import preprocessing
import score_model_helper
from sklearn.metrics import cohen_kappa_score
from sklearn.model_selection import KFold


# This class contains the model for scoring the essay, and includes functions
# for setting up and training the model.
class ScoreModel:
    # Initialize the model with one Embedding layer, one LSTM layer, and two Dense layers.
    # If you do not know what a LSTM is, see here:
    # https://colah.github.io/posts/2015-08-Understanding-LSTMs/.
    def __init__(self):
        self.tokenizer = Tokenizer()
        self.tokenizer.fit_on_texts(score_model_helper.get_dataframe('../data/training_set.tsv')['essay'])
        self.vocab_size = len(self.tokenizer.word_index) + 1

        self.model = Sequential()
        self.model.add(Embedding(self.vocab_size, 300, weights=[self.get_embedding_matrix()], input_length=200, trainable=False))
        self.model.add(LSTM(128, dropout=0.3, return_sequences=True))
        self.model.add(GlobalMaxPooling1D())
        self.model.add(Dense(64, activation='relu'))
        self.model.add(Dense(1, activation='sigmoid'))
        self.model.compile(loss='binary_crossentropy', optimizer='adam', metrics=['accuracy', 'mae'])
        self.model.summary()

    
    # Returns the model object (after it's been set up)
    def get_model(self):
        return self.model

    
    # Returns tokenizer
    def get_tokenizer(self):
        return self.tokenizer

    
    # Train the model to prime it for scoring essays, then test it using
    # an evaluation metric (in this case, Cohen's kappa coefficient)
    def train_and_test(self, data_loc):
        cv = KFold(n_splits=2, shuffle=True)
        results, y_pred_list = [], []  # Cohen's kappa coefficients

        x = score_model_helper.get_dataframe(data_loc)  # Training data
        y = x['domain1_score']

        count = 1
        # Using the "split" function, we split the data into
        # two parts: one for training and the other for testing. Then
        # we iterate the train/test procedure below five times, with 
        # each iteration improving upon the last.
        for traincv, testcv in cv.split(x):
            print("\n--------Fold {}--------\n".format(count))
            x_test, x_train, y_test, y_train = x.iloc[testcv], x.iloc[traincv], y.iloc[testcv], y.iloc[traincv] 

            train_essays = x_train['essay']  # Training essays
            test_essays = x_test['essay']  # Test essays

            # See score_model_helper.py file
            train_essays = score_model_helper.get_clean_essays(train_essays)
            test_essays = score_model_helper.get_clean_essays(test_essays)

            tokenizer = self.get_tokenizer()
            # Convert the text into a sequence of numbers (that the model can
            # understand)
            x_train_seq  = tokenizer.texts_to_sequences(train_essays)
            x_test_seq = tokenizer.texts_to_sequences(test_essays)

            # Pad the sequence to be of length 200
            x_train_seq = pad_sequences(x_train_seq, maxlen=200)
            x_test_seq = pad_sequences(x_test_seq, maxlen=200)

            # Turn sequences into numpy arrays
            x_train_seq = np.array(x_train_seq)
            x_test_seq = np.array(x_test_seq)

            # Train LSTM model
            lstm_model = self.get_model()
            lstm_model.fit(x_train_seq, y_train.values, batch_size=128, epochs=4)

            # Test LSTM model on test data
            y_pred = self.model.predict(x_test_seq)
            y_pred = np.around(y_pred * 100)
            y_test = np.around(y_test * 100)

            # Save the final iteration of the trained model
            if count == 2:
                lstm_model.save('./model_weights/final_lstm.h5')

            # Evaluate the model using Cohen's kappa coefficient
            result = cohen_kappa_score(y_test.values, y_pred, weights='quadratic')
            print("Cohen's kappa coefficient: {}".format(result))

            count += 1

    
    # Evaluate the input 'essay' on our trained model. See 'score_model_helper' file
    # for explanations of what the functions involved do.
    def evaluate(self, essay):
        tk = self.get_tokenizer()
        text_arr = score_model_helper.preprocess(essay, tk)
        text_arr = np.asarray(text_arr)
        lstm_model = self.get_model()
        lstm_model.load_weights('./model_weights/final_lstm.h5')  # Get weights from trained model
        score = lstm_model.predict(text_arr)[0, 0]  # Predict score of input essay
        return score * 100

    
    def test_evaluate(self):
        return


    # Used to build the Embedding layer
    def get_embedding_matrix(self):
        embeddings_index = {}
        f = open('glove6B/glove.6B.300d.txt', encoding='utf8')
        for line in f:
            values = line.split()
            word = values[0]
            coefs = np.asarray(values[1:], dtype='float32')
            embeddings_index[word] = coefs
        f.close()

        embedding_matrix = np.zeros((self.vocab_size, 300))
        for word, i in self.get_tokenizer().word_index.items():
            embedding_vector = embeddings_index.get(word)
            if embedding_vector is not None:
                embedding_matrix[i] = embedding_vector

        return embedding_matrix


score_model = ScoreModel()
score_model.train_and_test('../data/training_set_n.tsv')
score_model.test_evaluate()