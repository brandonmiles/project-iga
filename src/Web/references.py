import re


class ReferencesCheck:
    def extractCitation(self):
        self.lower()
        count = 0

        author = "(?:[A-Z][A-Za-z'`-]+)"
        etal = "(?:et al.?)"
        additional = "(?:,? (?:(?:and |& )?" + author + "|" + etal + "))"
        year_num = "(?:19|20)[0-9][0-9]"
        page_num = "(?:, p.? [0-9]+)?"
        year = "(?:, *" + year_num + page_num + "| *\(" + year_num + page_num + "\))"
        regex = "(" + author + additional + "*" + year + ")"

        matches = re.findall(regex, self)

        return matches

    def num_of_missing_citation(self):
        intext_citation = ReferencesCheck.extract_citation(self)
        reference_found = 0

        x = self.rfind("reference")
        if x:
            references = self[x:]
            for i in range(len(intext_citation)):
                if intext_citation[i].split(',')[0] in references:
                    reference_found += 1

        missing_citation = len(intext_citation) - reference_found

        return missing_citation
