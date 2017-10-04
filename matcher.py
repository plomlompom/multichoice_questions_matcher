#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# LICENSED UNDER THE GPL, EITHER VERSION 3, OR, AT YOUR OPTION, ANY LATER
# VERSION AS PUBLISHED BY THE FSF. FOR PROPRIETARY LICENSING, GIBE MONIES.
#
# forked from <http://daten.dieweltistgarnichtso.net/src/okmatchlib.py>


import unittest
import json


class MultiChoiceQuestion:

    def __init__(self, question, choices):

        # input validation
        if type(question) != str:
            raise TypeError('question must be string')
        if len(question) == 0:
            raise ValueError('question must be non-empty')
        if type(choices) not in {list, tuple}:
            raise TypeError('choices must be list or tuple')
        if len(choices) < 2:
            raise ValueError('choices must be of size >1')
        unique_choices = []
        for choice in choices:
            if choice in unique_choices:
                raise ValueError('choices must be unique')
            unique_choices += [choice]
            if type(choice) != str:
                raise TypeError('members of choices must be strings')
            if len(choice) == 0:
                raise ValueError('choices must be non-empty strings')

        # assignment
        self.question = question
        self.choices = list(choices)

    def __eq__(self, other):
        if type(other) != MultiChoiceQuestion:
            msg = 'can compare MultiChoiceQuestion only with same type'
            raise TypeError(msg)
        return self.question == other.question and \
            self.choices == other.choices


class Answer:
    def __init__(self, question, answer, acceptable_answers, importance):

        def validate_answer(answer):
            if type(answer) != int:
                raise TypeError('answer must be integer')
            if answer < 0 or answer >= len(question.choices):
                msg = 'answer must be >= 0 and < len(question.choices)'
                raise ValueError(msg)

        # input validation
        if type(question) != MultiChoiceQuestion:
            raise TypeError('question must be MultiChoiceQuestion')
        validate_answer(answer)
        if type(acceptable_answers) not in {tuple, list}:
            raise TypeError('acceptable_answers must be tuple or list')
        if len(acceptable_answers) == 0:
            raise ValueError('acceptable_answers must be non-empty')
        unique_acceptable_answers = []
        for a in acceptable_answers:
            if a in unique_acceptable_answers:
                raise ValueError('acceptable_answers must contain no doubles')
            unique_acceptable_answers += [a]
            validate_answer(a)
        if type(importance) != int:
            raise TypeError('importance must be integer')
        if importance < 0:
            raise ValueError('importance must be non-negative')

        # assignment
        self.question = question
        self.answer = answer
        self.acceptable_answers = list(acceptable_answers)
        self.importance = importance

    def __eq__(self, other):
        if type(other) != Answer:
            msg = 'can compare Answer only with same type'
            raise TypeError(msg)
        return self.question == other.question and \
            self.answer == other.answer and \
            self.acceptable_answers == other.acceptable_answers and \
            self.importance == other.importance


def match(answers_1, answers_2):
    """
    This function computes a match between two lists of Answers using
    the algorithm from <http://www.okcupid.com/help/match-percentages>.
    """

    # input validation
    for answers in (answers_1, answers_2):
        if type(answers) not in {list, tuple}:
            raise TypeError('answers must be list or tuple')
        unique_questions = []
        for answer in answers:
            if type(answer) != Answer:
                raise TypeError('answers must consist of Answer objects')
            if answer.question in unique_questions:
                raise ValueError('question answered more than once')
            unique_questions += [answer.question]

    # match calculation
    from math import sqrt
    shared_questions = 0
    answers_1_maxpoints = 0
    answers_2_maxpoints = 0
    answers_1_points = 0
    answers_2_points = 0
    for answer_1 in answers_1:
        for answer_2 in answers_2:
            if answer_1.question == answer_2.question:
                shared_questions += 1
                answers_1_maxpoints += answer_1.importance
                answers_2_maxpoints += answer_2.importance
                if answer_1.answer in answer_2.acceptable_answers:
                    answers_2_points += answer_2.importance
                if answer_2.answer in answer_1.acceptable_answers:
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


def parse_answers_list(answers_list_string):
    answers = []
    list_answers = json.loads(answers_list_string)
    if type(list_answers) != list:
        raise TypeError('answers not in array/list form')
    for entry in list_answers:
        if type(entry) != dict:
            raise TypeError('entry must be object/dict')
        if not set() == {'question', 'answer'} ^ set(entry.keys()):
            raise ValueError('entry keys must be "question", "answer"')
        if type(entry['question']) != dict:
            raise TypeError('question must be object/dict')
        if not set() == {'text', 'choices'} ^ set(entry['question'].keys()):
            raise ValueError('question keys must be "text", "choices"')
        if type(entry['answer']) != dict:
            raise TypeError('question must be object/dict')
        if not set() == {'choice',
                         'acceptable_answers',
                         'importance'} ^ set(entry['answer'].keys()):
            raise ValueError('answers keys must be "choice", '
                             '"acceptable_answers", "importance')
        q = MultiChoiceQuestion(entry['question']['text'],
                                entry['question']['choices'])
        a = Answer(q, entry['answer']['choice'],
                   entry['answer']['acceptable_answers'],
                   entry['answer']['importance'])
        answers += [a]
    return answers


class TestAll(unittest.TestCase):

    def test_question(self):
        self.assertRaises(TypeError, MultiChoiceQuestion, 0, ('0', '1'))
        self.assertRaises(ValueError, MultiChoiceQuestion, '', ('0', '1'))
        self.assertRaises(ValueError, MultiChoiceQuestion, '0', ('', '1'))
        self.assertRaises(ValueError, MultiChoiceQuestion, '0', ('0', '0'))
        self.assertRaises(TypeError, MultiChoiceQuestion, '0', ('0', 0))
        self.assertRaises(ValueError, MultiChoiceQuestion, '0', ())
        self.assertRaises(TypeError, MultiChoiceQuestion, '0', 0)

    def test_answer(self):
        q1 = MultiChoiceQuestion('Gender?',
                                 ('male', 'female', 'other'))
        self.assertRaises(TypeError, Answer, 0, 0, (0,), 0)
        self.assertRaises(TypeError, Answer, q1, 'x', (0,), 0)
        self.assertRaises(ValueError, Answer, q1, -1, (0,), 0)
        self.assertRaises(ValueError, Answer, q1, 3, (0,), 0)
        self.assertRaises(TypeError, Answer, q1, 0, 0, 0)
        self.assertRaises(TypeError, Answer, q1, 0, ('x'), 0)
        self.assertRaises(ValueError, Answer, q1, 0, (-1,), 0)
        self.assertRaises(ValueError, Answer, q1, 0, (3,), 0)
        self.assertRaises(TypeError, Answer, q1, 0, (0,), 'x')
        self.assertRaises(ValueError, Answer, q1, 0, (0, 0), 'x')
        self.assertRaises(ValueError, Answer, q1, 0, (0,), -1)

    def test_match(self):
        q1 = MultiChoiceQuestion('Gender?',
                                 ('male', 'female', 'other'))
        q2 = MultiChoiceQuestion('Do you like trains?',
                                 ('yes', 'no'))
        q3 = MultiChoiceQuestion('Best president?',
                                 ('Lincoln', 'Obama', 'Trump'))
        a1 = Answer(q1, 0, (0,), 100)
        a2 = Answer(q2, 0, (0,), 100)
        a3 = Answer(q3, 0, (0,), 100)
        self.assertRaises(TypeError, match, [], 0)
        self.assertRaises(TypeError, match, [], [0])
        self.assertRaises(ValueError, match, [a1, a1], [])
        self.assertEqual(match([], []), 0)
        self.assertEqual(match([a1], [a1]), 0)
        self.assertEqual(match([a1, a2], [a1]), 0)
        self.assertEqual(match([a1, a2], [a1, a2]), 0.5)
        answers_1 = [a1, a2, a3]
        answers_2 = [a1, a2, a3]
        self.assertEqual(match(answers_1, answers_2), 0.6666666666666667)
        answers_1 = [a1, a2, a3]
        answers_2 = [a1, a2]
        self.assertEqual(match(answers_1, answers_2), 0.5)
        a1 = Answer(q1, 0, (1, 2), 50)
        b1 = Answer(q1, 1, (1,), 25)
        a2 = Answer(q2, 0, (0,), 10)
        b2 = Answer(q2, 1, (0,), 10)
        a3 = Answer(q3, 0, (0,), 50)
        b3 = Answer(q3, 1, (0,), 70)
        answers_1 = [a1, a2]
        answers_2 = [b1, b2]
        self.assertEqual(match(answers_1, answers_2), 0)
        answers_1 = [a1, a2, a3]
        answers_2 = [b1, b2, b3]
        self.assertEqual(match(answers_1, answers_2), 0.25515655300316636)

    def test_parser(self):
        import copy
        self.assertRaises(TypeError, parse_answers_list, '0')
        self.assertRaises(TypeError, parse_answers_list, '{}')
        self.assertRaises(TypeError, parse_answers_list, '[0]')
        answer_list = [{
            'question': {
                'text': 'x',
                'choices': ['0', '1']
            },
            'answer': {
                'choice': 0,
                'acceptable_answers': [0],
                'importance':0}
            }
        ]
        bad = copy.deepcopy(answer_list)
        del bad[0]['question']['text']
        self.assertRaises(ValueError, parse_answers_list, json.dumps(bad))
        bad = copy.deepcopy(answer_list)
        del bad[0]['question']['choices']
        self.assertRaises(ValueError, parse_answers_list, json.dumps(bad))
        bad[0]['question'] = 0
        self.assertRaises(TypeError, parse_answers_list, json.dumps(bad))
        del bad[0]['question']
        self.assertRaises(ValueError, parse_answers_list, json.dumps(bad))
        bad = copy.deepcopy(answer_list)
        del bad[0]['answer']['choice']
        self.assertRaises(ValueError, parse_answers_list, json.dumps(bad))
        bad = copy.deepcopy(answer_list)
        del bad[0]['answer']['acceptable_answers']
        self.assertRaises(ValueError, parse_answers_list, json.dumps(bad))
        bad = copy.deepcopy(answer_list)
        del bad[0]['answer']['importance']
        self.assertRaises(ValueError, parse_answers_list, json.dumps(bad))
        bad[0]['answer'] = 0
        self.assertRaises(TypeError, parse_answers_list, json.dumps(bad))
        del bad[0]['answer']
        self.assertRaises(ValueError, parse_answers_list, json.dumps(bad))
        answers = parse_answers_list(json.dumps(answer_list))
        q_cmp = MultiChoiceQuestion('x', ['0', '1'])
        self.assertEqual(answers[0].question, q_cmp)
        a_cmp = Answer(q_cmp, 0, (0,), 0)
        self.assertEqual(answers[0], a_cmp)


if __name__ == '__main__':
    import sys
    import os.path
    if len(sys.argv) != 3:
        print('need precisely two filename arguments')
        exit(1)
    path_1 = sys.argv[1]
    path_2 = sys.argv[2]
    answers_lists = []
    for path in (path_1, path_2):
        if not os.path.isfile(path):
            print('no file at path:', path)
            exit(1)
        f = open(path, 'r')
        json_text = f.read()
        f.close()
        try:
            answers_lists += [parse_answers_list(json_text)]
        except json.decoder.JSONDecodeError as err:
            print('Trouble JSON-decoding answers file:', err)
            exit(1)
        except (ValueError, TypeError) as err:
            print('Malformed answers file:', err)
            exit(1)
    print(match(answers_lists[0], answers_lists[1]))
