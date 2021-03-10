def grammar_feedback(score, score_max):
    score = score / score_max * 4

    if score < 1:
        text = "Ineffective use of conventions of Standard English for grammar, usage, spelling, capitalization, " \
               "and punctuation."
    else:
        if score < 2:
            text = "Limited use of conventions of Standard English for grammar, usage, spelling, capitalization, " \
                   "and punctuation for the grade level."
        else:
            if score < 3:
                text = "Adequate use of conventions of Standard English for grammar, usage, spelling, capitalization," \
                       " and punctuation for the grade level."
            else:
                text = "Consistent, appropriate use of conventions of Standard English for grammar, usage, spelling, " \
                       "capitalization, and punctuation for the grade level."

    return text


def keyword_feedback(score, score_max):
    score = score / score_max * 4

    if score < 1:
        text = "Failed to include any keywords pertaining to the topic."
    else:
        if score < 2:
            text = "Only a few of the expected keywords used that are relevant to the subject."
        else:
            if score < 3:
                text = "Frequently used keywords relevant to the paper's topic"
            else:
                text = "Excellent use of topic keywords"

    return text


def length_feedback(score):
    text = "Failed to reduce the expected word count of the essay down to the word count maximum."

    if score == 0:
        text = "Failed to meet the minimum expected number of words for the essay."
    if score == 1:
        text = "Remained within the expected bounds of the word count."

    return text


def format_feedback(bool_list):
    text = ""

    if bool_list[0]:
        text = text + "Paper uses illegal font.\n"
    if bool_list[1]:
        text = text + "Paper uses illegal font size.\n"
    if bool_list[2]:
        text = text + "Line spacing is incorrect.\n"
    if bool_list[3]:
        text = text + "Spacing after every paragraph is incorrect.\n"
    if bool_list[4]:
        text = text + "Spacing before every paragraph is incorrect.\n"
    if bool_list[5]:
        text = text + "Paper width is incorrect.\n"
    if bool_list[6]:
        text = text + "Paper height is incorrect.\n"
    if bool_list[7]:
        text = text + "Paper margins are incorrect.\n"
    if bool_list[8]:
        text = text + "Paper margins are incorrect.\n"
    if bool_list[9]:
        text = text + "Paper margins are incorrect.\n"
    if bool_list[10]:
        text = text + "Paper margins are incorrect.\n"
    if bool_list[11]:
        text = text + "Header size is incorrect.\n"
    if bool_list[12]:
        text = text + "Footing Size is incorrect.\n"
    if bool_list[13]:
        text = text + "Gutter size is incorrect.\n"
    if bool_list[14]:
        text = text + "Paper indention is not correct.\n"
    if bool_list[15]:
        text = text + "Multiple paragraphs feature inconsistent margins compared to default margin.\n"
    if text == "":
        text = "Paper adheres to format standards correctly.\n"

    return text
