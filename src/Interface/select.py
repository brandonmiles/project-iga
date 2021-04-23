import pandas as pd
import numpy as np

data = pd.read_csv('./data/training_set.tsv', sep='\t', encoding='ISO-8859-1')
df = pd.DataFrame(data)
df1 = df.sample(n=500) # Select 500 random essays

perms = np.random.permutation(500)
parts = []
# Partition 500 random essays into 5 equal parts of 100 each
for i in range(5):
	parts.append(df1.iloc[perms[i::5]])

cols = ('essay_id', 'essay_set', 'essay', 'rater1_domain1', 'rater2_domain1', 'rater3_domain1', 
	'domain1_score', 'rater1_domain2', 'domain2_score', 'rater1_trait1', 'rater1_trait2', 'rater1_trait3',
	'rater1_trait4', 'rater1_trait5', 'rater1_trait6', 'rater2_trait1', 'rater2_trait2', 'rater2_trait3',
	'rater2_trait4', 'rater2_trait5', 'rater2_trait6', 'rater3_trait1', 'rater3_trait2', 'rater3_trait3',
	'rater3_trait4', 'rater3_trait5', 'rater3_trait6')

# Write results to CSV file
parts[0].to_csv('./data/feedback/gautam.csv', encoding='ISO-8859-1', columns=cols, index=False)
parts[1].to_csv('./data/feedback/jason.csv', encoding='ISO-8859-1', columns=cols, index=False)
parts[2].to_csv('./data/feedback/nathan.csv', encoding='ISO-8859-1', columns=cols, index=False)
parts[3].to_csv('./data/feedback/sujan.csv', encoding='ISO-8859-1', columns=cols, index=False)
parts[4].to_csv('./data/feedback/brandon.csv', encoding='ISO-8859-1', columns=cols, index=False)