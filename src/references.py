import re
import nltk
import nltk
from nltk import word_tokenize

# nltk.download('averaged_perceptron_tagger')
# nltk.download('maxent_ne_chunker')
# nltk.download('words')


# Returns number of missing references
def extract_citation(text):
    matches = re.findall(r'\(.*?\)', text)  # extract everything inside a '()'
    keywords = []  # store named entities
    names = []  # store names
    found_references, missing_references = [], []

    for i in range(len(matches)):
        NE_tokens = word_tokenize(matches[i])
        NE_tags = nltk.pos_tag(NE_tokens)
        NE_NER = nltk.ne_chunk(NE_tags)

        # only save a person or organization in keywords
        for t in NE_NER.subtrees():
            if t.label() == 'PERSON' or t.label() == 'ORGANIZATION':
                keywords.append(list(t))

    # extract the names from keywords
    for i in range(len(keywords)):
        names.append(keywords[i][0][0])

    x = text.rfind("Reference")
    if x:
        references = text[x:].lower()
        for i in range(len(names)):
            if names[i].lower() in references:
                found_references.append(names[i])
            else:
                missing_references.append(names[i])

    # print(found_references)

    return len(missing_references)
