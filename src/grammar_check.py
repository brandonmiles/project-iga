import pandas
import language_tool_python

tool = language_tool_python.LanguageTool('en-US')


def number_of_errors(text):
    pair = []

    matches = tool.check(text)

    for rules in matches:
        if len(rules.replacements) > 0:
            pair.append((text[rules.offset:rules.errorLength + rules.offset], rules.replacements[0]))

    text = tool.correct(text)
    matches = tool.check(text)

    for rules in matches:
        if len(rules.replacements) > 0:
            pair.append((text[rules.offset:rules.errorLength + rules.offset], rules.replacements[0]))

    text = tool.correct(text)

    return pair, text

