import re


class ReferencesCheck:
    def extractCitation(self):
        count = 0

        author = "(?:[A-Z][A-Za-z'`-]+)"
        etal = "(?:et al.?)"
        additional = "(?:,? (?:(?:and |& )?" + author + "|" + etal + "))"
        year_num = "(?:19|20)[0-9][0-9]"
        page_num = "(?:, p.? [0-9]+)?"  # Always optional
        year = "(?:, *" + year_num + page_num + "| *\(" + year_num + page_num + "\))"
        regex = "(" + author + additional + "*" + year + ")"

        matches = re.findall(regex, self)
        matches = list(dict.fromkeys(matches))
        matches.sort()

        count = len(matches)

        return matches, count
