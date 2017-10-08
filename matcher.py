#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# LICENSED UNDER THE GPL, EITHER VERSION 3, OR, AT YOUR OPTION, ANY LATER
# VERSION AS PUBLISHED BY THE FSF. FOR PROPRIETARY LICENSING, GIBE MONIES.
#
# forked from <http://daten.dieweltistgarnichtso.net/src/okmatchlib.py>


import unittest
import jsonschema
import matchlib


class TestAll(unittest.TestCase):

    def test_match(self):

        def match_prepared(l1, l2):
            return match(matchlib.AnswersList(answers=l1),
                         matchlib.AnswersList(answers=l2))

        q1 = matchlib.MultiChoiceQuestion('x', ('0', '1', '2'))
        q2 = matchlib.MultiChoiceQuestion('x', ('0', '1'))
        q3 = matchlib.MultiChoiceQuestion('y', ('0', '1', '2'))
        a1 = matchlib.Answer(q1, 0, (0,), 100)
        a2 = matchlib.Answer(q2, 0, (0,), 100)
        a3 = matchlib.Answer(q3, 0, (0,), 100)
        self.assertEqual(match_prepared([], []), 0)
        self.assertEqual(match_prepared([a1], []), 0)
        self.assertEqual(match_prepared([a1], [a1]), 0)
        self.assertEqual(match_prepared([a1, a2], [a1]), 0)
        self.assertEqual(match_prepared([a1, a2], [a1, a2]), 0.5)
        self.assertEqual(match_prepared([a1, a2, a3], [a1, a2, a3]),
                         0.6666666666666667)
        self.assertEqual(match_prepared([a1, a2, a3], [a1, a2]), 0.5)
        a1 = matchlib.Answer(q1, 0, (1, 2), 50)
        b1 = matchlib.Answer(q1, 1, (1,), 25)
        a2 = matchlib.Answer(q2, 0, (0,), 10)
        b2 = matchlib.Answer(q2, 1, (0,), 10)
        a3 = matchlib.Answer(q3, 0, (0,), 50)
        b3 = matchlib.Answer(q3, 1, (0,), 70)
        self.assertEqual(match_prepared([a1, a2], [b1, b2]), 0)
        self.assertEqual(match_prepared([a1, a2, a3], [b1, b2, b3]),
                         0.25515655300316636)


def match(answers_1, answers_2):
    """
    This function computes a match between two lists of Answers using
    the algorithm from <http://www.okcupid.com/help/match-percentages>.
    """
    from math import sqrt
    shared_questions = 0
    answers_1_maxpoints = 0
    answers_2_maxpoints = 0
    answers_1_points = 0
    answers_2_points = 0
    for answer_1 in answers_1.question_answer_complexes:
        for answer_2 in answers_2.question_answer_complexes:
            if answer_1.question == answer_2.question:
                shared_questions += 1
                answers_1_maxpoints += answer_1.importance
                answers_2_maxpoints += answer_2.importance
                if answer_1.choice in answer_2.acceptable_choices:
                    answers_2_points += answer_2.importance
                if answer_2.choice in answer_1.acceptable_choices:
                    answers_1_points += answer_1.importance
                break
    match_1 = 0
    if answers_1_maxpoints > 0:
        match_1 = answers_1_points / answers_1_maxpoints
    match_2 = 0
    if answers_2_maxpoints > 0:
        match_2 = answers_2_points / answers_2_maxpoints
    error_margin = 1
    if shared_questions > 0:
        error_margin = 1 / shared_questions
    match_both = max(0, sqrt(match_1 * match_2) - error_margin)
    return match_both




if __name__ == '__main__':
    import os.path
    import argparse
    argparser = argparse.ArgumentParser()
    argparser.add_argument('answers_files', nargs=2, metavar='FILEPATH',
                           help='one of both answers files which to compare')
    args = argparser.parse_args()
    answers_lists = []
    for path in args.answers_files:
        if not os.path.isfile(path):
            print('no file at path:', path)
            exit(1)
        try:
            answers_list = matchlib.AnswersList(path=path)
        except matchlib.AnswersParseError as err:
            print(err)
            exit(1)
        answers_lists += [answers_list]
    print(match(answers_lists[0], answers_lists[1]))
