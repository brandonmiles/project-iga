import pandas
import language_tool_python

tool = language_tool_python.LanguageTool('en-US')


def number_of_errors(text):
    """
    Used to both correct the given text of errors as well as return a list of all grammar and spelling errors. Note that
    the text is run through the grammar and spelling check twice for greater accuracy.

    Parameters
    ----------
    text : str
        The text you want to check for grammar and spelling.

    Returns
    -------
    tuple
        The tuple consists of a list and the corrected text.
        The list contains the pairs of the error and the suggested correction.
        The corrected text is a string file of raw text.
    """
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
