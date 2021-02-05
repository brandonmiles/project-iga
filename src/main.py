import nltk
import spellcheck

spell = spellcheck.SpellCheck()
file = open('../data/test_set.tsv', encoding='ansi')

token = nltk.word_tokenize(file.read(10000))  # Trying to read the whole file is gonna take a while, don't do it
number, errors = spell.number_of_errors(token)
print(number)
print(errors)
