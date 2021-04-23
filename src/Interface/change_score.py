import pandas as pd

train_data = pd.read_csv('./data/training_set.tsv', sep='\t', encoding='ISO-8859-1')

# Get minimum score for given essay set
def get_min(etype):
	if (etype == 1): return 2
	if (etype == 2): return 1
	return 0 # type > 2


# Get maximum score for given essay set
def get_max(etype):
	if (etype == 1): return 12
	if (etype == 2): return 6
	if (etype == 3 or etype == 4): return 3
	if (etype == 5 or etype == 6): return 4
	if (etype == 7): return 30
	return 60 # type == 8


# Normalize scores to be between 0 and 1
for idx, row in train_data.iterrows():
	i = row['essay_set']
	j = row['domain1_score']
	mini = get_min(i)
	maxi = get_max(i)
	new_score = (j - mini) / (maxi - mini)
	train_data.loc[idx, 'domain1_score'] = new_score


train_data.to_csv('./data/training_set_n.tsv', sep='\t', encoding='ISO-8859-1', index=False)