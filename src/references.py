import re
import nltk
from nltk import word_tokenize


def extract_citation(text):
    """
    Returns the total number of references missing in the references section of the given essay
    
    Parameters
    ----------
    text : str
        The text you want to check for references.
    Returns
    -------
    integer
        The total number of missing references in the provided text.
    """
    
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
    
    # find the last instance of the word 'reference', this is where the list of references start
    text = text.lower()
    x = text.rfind("reference")
    if x:
        references = text[x:]
        for i in range(len(names)):
            if names[i].lower() in references:
                found_references.append(names[i])
            else:
                missing_references.append(names[i])

    return len(missing_references)
