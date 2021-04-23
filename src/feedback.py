def grammar_feedback(score):
    """
    When given an integer input between 0 and 3 (inclusive), grammar_feedback() will return a pre-made comment where 0
    is the best comment and 3 is the worst.

    Parameters
    ----------
    score : int
        Must be between 0 and 3, any other integer will cause the best comment to be used by default.

    Returns
    -------
    str
        A pre-made comment regarding the quality of the essays grammar and spelling.
    """
    if score == 3:
        text = "Ineffective use of conventions of Standard English for grammar, usage, spelling, capitalization, " \
               "and punctuation.\n"
    else:
        if score == 2:
            text = "Limited use of conventions of Standard English for grammar, usage, spelling, capitalization, " \
                   "and punctuation for the grade level.\n"
        else:
            if score == 1:
                text = "Adequate use of conventions of Standard English for grammar, usage, spelling, capitalization," \
                       " and punctuation for the grade level.\n"
            else:
                text = "Consistent, appropriate use of conventions of Standard English for grammar, usage, spelling, " \
                       "capitalization, and punctuation for the grade level.\n"

    return text


def keyword_feedback(score):
    """
    When given an integer input between 0 and 3 (inclusive), keyword_feedback() will return a pre-made comment where 0
    is the best comment and 3 is the worst.

    Parameters
    ----------
    score : int
        Must be between 0 and 3, any other integer will cause the best comment to be used by default.

    Returns
    -------
    str
        A pre-made comment regarding the number of keywords used in the essay.
    """
    if score == 3:
        text = "Failed to include any keywords pertaining to the topic.\n"
    else:
        if score == 2:
            text = "Only a few of the expected keywords used that are relevant to the subject.\n"
        else:
            if score == 1:
                text = "Frequently used keywords relevant to the paper's topic.\n"
            else:
                text = "Excellent use of topic keywords.\n"

    return text


def length_feedback(score):
    """
    When given an integer input between 0 and 2 (inclusive), length_feedback() will return a pre-made comment where 0
    is meeting the length requirement, 1 is going over the maximum length, and 2 is going under the minimum length.

    Parameters
    ----------
    score : int
        Must be between 0 and 2, any other integer will cause the best comment to be used by default.

    Returns
    -------
    str
        A pre-made comment regarding overall length of the essay.
    """
    if score == 2:
        text = "Failed to meet the minimum expected number of words for the essay.\n"
    else:
        if score == 1:
            text = "Failed to reduce the expected word count of the essay down to the word count maximum.\n"
        else:
            text = "Remained within the expected bounds of the word count.\n"

    return text


def format_feedback(bool_list):
    """
    When given a bool list with a length of at least 16, format_feedback() will check for any entries set to true and
    compile a comment of all of the format errors.

    Parameters
    ----------
    bool_list :list of bool
        Must be a bool list of at least 16 length.

    Returns
    -------
    str
        A pre-made comment regarding the exact kind of format errors were found.
    """
    text = ""

    if bool_list[0]:
        text += "Paper uses illegal font.\n"
    if bool_list[1]:
        text += "Paper uses illegal font size.\n"
    if bool_list[2]:
        text += "Line spacing is incorrect.\n"
    if bool_list[3]:
        text += "Spacing after every paragraph is incorrect.\n"
    if bool_list[4]:
        text += "Spacing before every paragraph is incorrect.\n"
    if bool_list[5]:
        text += "Paper width is incorrect.\n"
    if bool_list[6]:
        text += "Paper height is incorrect.\n"
    if bool_list[7]:
        text += "Paper margins are incorrect.\n"
    if bool_list[8]:
        text += "Paper margins are incorrect.\n"
    if bool_list[9]:
        text += "Paper margins are incorrect.\n"
    if bool_list[10]:
        text += "Paper margins are incorrect.\n"
    if bool_list[11]:
        text += "Header size is incorrect.\n"
    if bool_list[12]:
        text += "Footing Size is incorrect.\n"
    if bool_list[13]:
        text += "Gutter size is incorrect.\n"
    if bool_list[14]:
        text += "Paper indention is not correct.\n"
    if bool_list[15]:
        text += "Multiple paragraphs feature inconsistent margins compared to default margin.\n"
    if text == "":
        text = "Paper adheres to format standards correctly.\n"

    return text


def reference_feedback(score):
    """
    When given an integer input between 0 and 2 (inclusive), reference_feedback() will return a pre-made comment where 0
    is the best comment and 2 is the worst.

    Parameters
    ----------
    score : int
        Must be between 0 and 2, any other integer will cause the best comment to be used by default.

    Returns
    -------
    str
        A pre-made comment regarding how many references were found or missing.
    """

    if score == 2:
        text = "Some references were missing\n"
    else:
        if score == 1:
            text = "Failed to properly reference a majority of the text\n"
        else:
            text = "All references found\n"
    return text


def idea_feedback(score):
    """
    When given an integer input between 0 and 2 (inclusive), idea_feedback() will return a pre-made comment where 0
    is the best comment and 2 is the worst.

    Parameters
    ----------
    score : int
        Must be between 0 and 2, any other integer will cause the best comment to be used by default.

    Returns
    -------
    str
        A pre-made comment regarding the quality of the ideas presented in the essay.
    """
    if score == 2:
        text = "The ideas presented in the essay have little to no relevance to the topic. There are few, if any, " \
               "details that are connected to the ideas presented.\n"
    else:
        if score == 1:
            text = "The ideas presented in the essay are on-topic, but the ideas and the details relating to them are" \
                   " not necessarily well-presented.\n"
        else:
            text = "The ideas presented in the essay are on-topic and well-presented. The details are specific and " \
                   "clearly connected to the ideas.\n"
    return text


def organization_feedback(score):
    """
    When given an integer input between 0 and 2 (inclusive), organization_feedback() will return a pre-made comment
    where 0 is the best comment and 2 is the worst.

    Parameters
    ----------
    score : int
        Must be between 0 and 2, any other integer will cause the best comment to be used by default.

    Returns
    -------
    str
        A pre-made comment regarding the quality of the overall organization in the essay.
    """

    if score == 2:
        text = "The flow of the essay lacks smoothness, and the connections between sentences are often not clear.\n"
    else:
        if score == 1:
            text = "The flow of the essay is smooth, but rocky at some points. The connections between sentences are " \
                   "typically clear and logical.\n"
        else:
            text = "The flow of the essay is smooth. There are clear and logical connections between sentences.\n"

    return text


def style_feedback(score):
    """
    When given an integer input between 0 and 2 (inclusive), style_feedback() will return a pre-made comment where 0 is
    the best comment and 2 is the worst.

    Parameters
    ----------
    score : int
        Must be between 0 and 2, any other integer will cause the best comment to be used by default.

    Returns
    -------
    str
        A pre-made comment regarding the overall style of the essay.
    """

    if score == 2:
        text = "The author has poor command of their language. Sentence structure and/or vocabulary usage is " \
               "repetitive, and/or the author’s language does not support their purpose.\n"
    else:
        if score == 1:
            text = "The author has adequate command of their language. Sentence structure and vocabulary usage are " \
                   "effective at communicating the author’s purpose.\n"
        else:
            text = "The author has total command of their language. Sentence structure and vocabulary usage is " \
                   "varied, and the author effectively uses language to support their purpose.\n"

    return text
