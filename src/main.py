import nltk
import spellcheck

spell = spellcheck.SpellCheck('../data/exceptions.txt')

try:
    file = open('../data/test_set.tsv', encoding='ansi')
except FileNotFoundError:
    print("File does not exist")
    
token = nltk.word_tokenize(file.read(1000))  # Trying to read the whole file is gonna take a while, don't do it
number, errors = spell.number_of_errors(token)
print(number)
print(errors)

if not spell.add_exception('essay_set'):  # Demonstrating the ability to add exceptions
    print('Error in adding exception')

number, errors = spell.number_of_errors(token)
print(number)
print(errors)
