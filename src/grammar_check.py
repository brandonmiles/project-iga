import pandas
import language_tool_python

tool = language_tool_python.LanguageTool('en-US')


class GrammarCheck:

    def number_of_errors(self):
        count = 0
        mistakes = []
        corrections = []

        matches = tool.check(self)
        count = len(matches)

        for rules in matches:
            if len(rules.replacements) > 0:
                mistakes.append(self[rules.offset:rules.errorLength + rules.offset])
                corrections.append(rules.replacements[0])

        return count, mistakes, corrections
