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
                       " and punctuation for the grade level. "
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
