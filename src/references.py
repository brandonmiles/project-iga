import re

import nltk
from nltk import word_tokenize


class ReferencesCheck:
    def extract_citation(self):
        matches = re.findall(r'\(.*?\)', self)  # extract everything inside a '()'
        keywords = []  # store named entities
        names = []  # store names

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

        return matches, names  # return matches and names

    def num_of_missing_citation(self):
        in_text, names = ReferencesCheck.extract_citation(self)
        found_references = []
        missing_references = []

        x = self.rfind("Reference")
        if x:
            references = self[x:].lower()
            for i in range(len(names)):
                if names[i].lower() in references:
                    found_references.append(names[i])
                else:
                    missing_references.append(names[i])

        missing_citation = len(missing_references)

        #print(missing_references)
        #print(found_references)

        return missing_citation
