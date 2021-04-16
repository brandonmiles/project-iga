import pandas as pd
import mysql.connector as mysql
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score
from sklearn.neural_network import MLPClassifier

# Previous attempts used these
# from sklearn.naive_bayes import BernoulliNB
# from sklearn.linear_model import LogisticRegression

# database info
HOST = "database-1.cluster-cf5kjev2ovc7.us-east-1.rds.amazonaws.com"
Database = "IGA_DB"
USER = 'admin'
PASSWORD = '8m8oqtTn'

# Connect to database (will only work when database is running)
conn = mysql.connect(host=HOST, database=Database, user=USER, password=PASSWORD)
cursor = conn.cursor()

# Get all rows from feedback table, contains feedback for all essays with scores
cursor.execute("SELECT essay, feedback FROM Feedback, TrainingEssays WHERE Feedback.essay_id_fk = TrainingEssays.essay_id;")
results = cursor.fetchall()
# Convert results to a pandas dataframe
df = pd.DataFrame(results, columns=['essay', 'feedback'])
# don't need database connection anymore
conn.close()

# convert feedback column to categorical data
df['feedback'] = df['feedback'].astype('category')

# set up predictor (X) and target (y)
X = df.essay
y = df.feedback
# split essays into training and testing groups
X_train, X_test, y_train, y_test = train_test_split(X, y, train_size=0.8, random_state=1234)

# remove stop words and perform vectorization
vectorizer = TfidfVectorizer(stop_words='english', ngram_range=(1, 2), max_features=1200)
X_train = vectorizer.fit_transform(X_train)
X_test = vectorizer.transform(X_test)

# train using a neural network
#classifier = LogisticRegression(max_iter=200)
classifier = MLPClassifier(hidden_layer_sizes=(300, 64, 5), random_state=1, max_iter=2000)
classifier.fit(X_train, y_train)

# make predictions on test data, print accuracy score
pred = classifier.predict(X_test)
print('Accuracy:', accuracy_score(y_test, pred))
