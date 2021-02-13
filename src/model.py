from keras.models import Sequential
from keras.layers import Dense
from keras.layers import LSTM
from keras.layers import Dropout
import pandas as pd

class Model:
	# Initialize the model
	#
	# num_units: Number of units in the LSTM
	# num_layers: Number of layers in the network following the LSTM
	def __init__(self, num_units, num_layers):
		self.model = Sequential()
		# TODO: Fix this mess.
		self.model.add(LSTM(300, dropout=0.4, recurrent_dropout=0.4, input_shape=(300, 1), return_sequences=True))
		self.model.add(LSTM(64, input_shape=(64, 10, 1), recurrent_dropout=0.4))
		self.model.add(Dropout(0.5))
		self.model.add(Dense(1, input_shape=(64, 1), activation='relu'))
		self.model.compile(loss='mean_squared_error', optimizer='rmsprop', metrics=['accuracy'])
		self.model.summary()

	# TODO: Move this to another file.
	def get_dataframe(self, data_loc):
		df = pd.read_csv(data_loc, sep='\t', encoding='ISO-8859-1')
		df = df.dropna(axis=1)
		if ('training_set' in data_loc):
			df = df.drop(columns=['rater1_domain1', 'rater2_domain1'])
			df = df.drop(columns=['essay_id', 'essay_set'])
		return df

	def train(self, training_data, batch_size, num_epochs):
		print(training_data['essay'].shape)
		self.model.fit(training_data['essay'], training_data['domain1_score'],
			batch_size=batch_size, epochs=num_epochs)

	def test(self, test_data):
		self.model.predict(test_data['essay'])