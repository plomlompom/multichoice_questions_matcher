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
            return match(matchlib.AnsweredQuestionsList(aqs=l1),
                         matchlib.AnsweredQuestionsList(aqs=l2))

        q1 = matchlib.MultiChoiceQuestion('x', ('0', '1', '2'))
        q2 = matchlib.MultiChoiceQuestion('x', ('0', '1'))
        q3 = matchlib.MultiChoiceQuestion('y', ('0', '1', '2'))
        a1 = matchlib.AnsweredQuestion(q1, 0, (0,), 100)
        a2 = matchlib.AnsweredQuestion(q2, 0, (0,), 100)
        a3 = matchlib.AnsweredQuestion(q3, 0, (0,), 100)
        self.assertEqual(match_prepared([], []), 0)
        self.assertEqual(match_prepared([a1], []), 0)
        self.assertEqual(match_prepared([a1], [a1]), 0)
        self.assertEqual(match_prepared([a1, a2], [a1]), 0)
        self.assertEqual(match_prepared([a1, a2], [a1, a2]), 0.5)
        self.assertEqual(match_prepared([a1, a2, a3], [a1, a2, a3]),
                         0.6666666666666667)
        self.assertEqual(match_prepared([a1, a2, a3], [a1, a2]), 0.5)
        a1 = matchlib.AnsweredQuestion(q1, 0, (1, 2), 50)
        b1 = matchlib.AnsweredQuestion(q1, 1, (1,), 25)
        a2 = matchlib.AnsweredQuestion(q2, 0, (0,), 10)
        b2 = matchlib.AnsweredQuestion(q2, 1, (0,), 10)
        a3 = matchlib.AnsweredQuestion(q3, 0, (0,), 50)
        b3 = matchlib.AnsweredQuestion(q3, 1, (0,), 70)
        self.assertEqual(match_prepared([a1, a2], [b1, b2]), 0)
        self.assertEqual(match_prepared([a1, a2, a3], [b1, b2, b3]),
                         0.25515655300316636)


def match(aqs_1, aqs_2):
    """
    This function computes a match between two lists of AnsweredQuestions using
    the algorithm from <http://www.okcupid.com/help/match-percentages>.
    """
    from math import sqrt
    shared_questions = 0
    aqs_1_maxpoints = 0
    aqs_2_maxpoints = 0
    aqs_1_points = 0
    aqs_2_points = 0
    for aq_1 in aqs_1.db:
        for aq_2 in aqs_2.db:
            if aq_1.question == aq_2.question:
                shared_questions += 1
                aqs_1_maxpoints += aq_1.importance
                aqs_2_maxpoints += aq_2.importance
                if aq_1.choice in aq_2.acceptable:
                    aqs_2_points += aq_2.importance
                if aq_2.choice in aq_1.acceptable:
                    aqs_1_points += aq_1.importance
                break
    match_1 = 0
    if aqs_1_maxpoints > 0:
        match_1 = aqs_1_points / aqs_1_maxpoints
    match_2 = 0
    if aqs_2_maxpoints > 0:
        match_2 = aqs_2_points / aqs_2_maxpoints
    error_margin = 1
    if shared_questions > 0:
        error_margin = 1 / shared_questions
    match_both = max(0, sqrt(match_1 * match_2) - error_margin)
    return match_both


def print_analysis(aqs_1, aqs_2):
    len_shared_questions = 0
    print('Matching table column legend:')
    print('c: person 1 chooses this answer')
    print('C: person 2 chooses this answer')
    print('a: person 1 accepts this as a valid choice for person 2')
    print('A: person 2 accepts this as a valid choice for person 1')
    print('==================================')
    for aq_1 in sorted(aqs_1.db, key=lambda aq: aq.importance, reverse=True):
        for aq_2 in aqs_2.db:
            if aq_1.question == aq_2.question:
                len_shared_questions += 1
                print(aq_1.question.prompt)
                print()
                print('c|a|C|A|answer')
                print('-+-+-+-+--------')
                for i, selectable in enumerate(aq_1.question.selectables):
                    chosen_1 = 'x|' if i == aq_1.choice else ' |'
                    chosen_2 = 'x|' if i == aq_2.choice else ' |'
                    acceptable_1 = 'x|' if i in aq_1.acceptable else ' |'
                    acceptable_2 = 'x|' if i in aq_2.acceptable else ' |'
                    print(chosen_1 + acceptable_1 + chosen_2 + acceptable_2 +
                          selectable)
                print()
                print('Person 1 assigns importance %s to choice of person 2.' %
                      aq_1.importance)
                print('Person 2 assigns importance %s to choice of person 1.' %
                      aq_2.importance)
                print('==================================')
                break
    questions_1_len = len(aqs_1.unique_questions)
    questions_2_len = len(aqs_2.unique_questions)
    print('Matched questions:', len_shared_questions)
    print('Non-matched questions from 1:',
          questions_1_len - len_shared_questions)
    print('Non-matched questions from 2:',
          questions_2_len - len_shared_questions)
    print('Overall match:',
          str(round(match(aqs_lists[0], aqs_lists[1]) * 100)) + '%')


if __name__ == '__main__':
    import os.path
    import argparse
    import urllib
    argparser = argparse.ArgumentParser()
    argparser.add_argument('aqs_files', nargs=2,
                           metavar='PATH',
                           help='location of one of both answered questions '
                                'files which to compare; may be local file '
                                'path or URL')
    args = argparser.parse_args()
    aqs_lists = []
    for i, path in enumerate(args.aqs_files):
        if urllib.parse.urlparse(path).scheme != '':
            try:
                path, _ = urllib.request.urlretrieve(path)
            except (ValueError, urllib.error.HTTPError) as err:
                print('trouble retrieving file:', err)
                exit(1)
        if not os.path.isfile(path):
            print('no file at path:', path)
            exit(1)
        try:
            aqs_list = matchlib.AnsweredQuestionsList(path=path)
        except matchlib.AnsweredQuestionsParseError as err:
            print(path + ':', err)
            exit(1)
        aqs_lists += [aqs_list]
    print_analysis(aqs_lists[0], aqs_lists[1])
