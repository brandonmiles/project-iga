import model
import nltk
import spellcheck

spell = spellcheck.SpellCheck()
test_file = open('../data/test_set.tsv', encoding='ansi')
#train_file = open('../data/training_set.tsv', encoding='ansi')
#valid_file = open('../data/valid_set.tsv', encoding='ansi')

test_token = nltk.word_tokenize(test_file.read(10000))  # Trying to read the whole file is gonna take a while, don't do it
number, errors = spell.number_of_errors(token)
print(number)
print(errors)

#mod = model.Model(100, 1)
#mod.train(mod.get_dataframe('../data/training_set.tsv'), 64, 2)
#mod.test(mod.get_dataframe('../data/test_set.tsv'))