from score_model import ScoreModel

import pandas as pd
import spellcheck
import grammar_check

spell = spellcheck.SpellCheck('../data/exceptions.tsv')

try:
	test_data = pd.read_csv('../data/test_set.tsv', sep='\t', encoding='ISO-8859-1')
	# Table column names are "essay_id", "essay_set", "essay", "domain1_predictionid", "domain2_predictionid"

	# Uncomment if you want to run the model.
	model = ScoreModel()
	model.train_and_test('../data/training_set.tsv')

	#for i in range(len(test_data['essay'])):
		#number, errors = spell.number_of_errors(test_data['essay'][i])
		#print("Essay: ", i, " Errors: ", number)
		#print(errors)

	# Grammar Check
	#for i in range(len(test_data['essay'])):
		#number, mistakes, corrections = grammar_check.GrammarCheck.number_of_errors(test_data['essay'][i])
		#print("Essay: ", i, "Errors: ", number)
		#print(list(zip(mistakes, corrections)))

except FileNotFoundError:
	print("File does not exist")
