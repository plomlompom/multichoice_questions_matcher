#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# LICENSED UNDER THE GPL, EITHER VERSION 3, OR, AT YOUR OPTION, ANY LATER
# VERSION AS PUBLISHED BY THE FSF. FOR PROPRIETARY LICENSING, GIBE MONIES.
#
# forked from <http://daten.dieweltistgarnichtso.net/src/okmatchlib.py>


import unittest
import jsonschema


schema = {
    '$schema': 'http://json-schema.org/schema#',
    'title': 'answer set',
    'type': 'array',
    'items': {
        'type': 'object',
        'properties': {
            'question_prompt': {
                'type': 'string',
                'minLength': 1
            },
            'available_answers': {
                'type': 'array',
                'items': {
                    'properties': {
                        'answer_text': {
                            'type': 'string',
                            'minLength': 1
                        },
                        'chosen': {
                            'type': 'boolean',
                            'default': False
                        },
                        'acceptable': {
                            'type': 'boolean',
                            'default': False
                        }
                    },
                    'required': ['answer_text'],
                    'additionalProperties': False
                },
                'minItems': 2
            },
            'importance': {
                'type': 'integer',
                'minimum': 0
            }
        },
        'required': ['question_prompt', 'available_answers', 'importance'],
        'additionalProperties': False
    }
}


class MultiChoiceQuestion:

    def __init__(self, question_prompt, available_answers):
        unique_answers = []
        for answer in available_answers:
            if answer in unique_answers:
                raise ValueError('duplicate available answer text: ' + answer)
            unique_answers += [answer]
        self.prompt = question_prompt
        self.answers = available_answers

    def __eq__(self, other):
        if type(other) != MultiChoiceQuestion:
            msg = 'can compare MultiChoiceQuestion only with same type'
            raise TypeError(msg)
        return self.prompt == other.prompt and self.answers == other.answers


class AnswersList:

    def __init__(self, d):
        jsonschema.validate(d, schema)
        self.question_answer_complexes = []
        unique_questions = []
        for answer in d:
            available_answer_texts = []
            choice = -1
            acceptable_choices = []
            for i in range(len(answer['available_answers'])):
                available_answer = answer['available_answers'][i]
                available_answer_texts += [available_answer['answer_text']]
                if 'chosen' in available_answer and available_answer['chosen']:
                    if choice > -1:
                        raise ValueError('more than one answer thosen')
                    choice = i
                if 'acceptable' in available_answer and \
                        available_answer['acceptable']:
                    acceptable_choices += [i]
            if choice == -1:
                raise ValueError('no answer chosen')
            question = MultiChoiceQuestion(answer['question_prompt'],
                                           available_answer_texts)
            if question in unique_questions:
                raise ValueError('question answered more than once')
            unique_questions += [question]
            self.question_answer_complexes += [{
                'question': question,
                'choice': choice,
                'acceptable_choices': acceptable_choices,
                'importance': answer['importance'],
            }]


class TestAll(unittest.TestCase):

    def test_answerlist_validation(self):
        from functools import partial
        from copy import deepcopy
        schema_fail = partial(self.assertRaises,
                              jsonschema.exceptions.ValidationError,
                              AnswersList)
        value_fail = partial(self.assertRaises, ValueError, AnswersList)
        schema_fail({})
        AnswersList([])
        schema_fail([{}])
        schema_fail([0])
        good = [{
          "question_prompt": "?",
          "available_answers": [{
            "answer_text": "0",
            "chosen": False,
            "acceptable": True
            }, {
            "answer_text": "1",
            "chosen": True,
            "acceptable": True
          }],
          "importance": 0
        }]
        AnswersList(good)
        bad = deepcopy(good)
        del bad[0]['available_answers'][0]
        schema_fail(bad)
        bad = deepcopy(good)
        bad[0]['question_prompt'] = 0
        schema_fail(bad)
        bad[0]['question_prompt'] = ''
        schema_fail(bad)
        del bad[0]['question_prompt']
        schema_fail(bad)
        bad = deepcopy(good)
        bad[0]['importance'] = 'x'
        schema_fail(bad)
        bad[0]['importance'] = 3.14
        schema_fail(bad)
        bad[0]['importance'] = -1
        schema_fail(bad)
        del bad[0]['importance']
        schema_fail(bad)
        bad = deepcopy(good)
        bad[0]['available_answers'][0]['answer_text'] = 0
        schema_fail(bad)
        bad[0]['available_answers'][0]['answer_text'] = ''
        schema_fail(bad)
        del bad[0]['available_answers'][0]['answer_text']
        schema_fail(bad)
        bad = deepcopy(good)
        bad[0]['available_answers'][0]['chosen'] = 'x'
        schema_fail(bad)
        bad = deepcopy(good)
        bad[0]['available_answers'][0]['acceptable'] = 'x'
        schema_fail(bad)
        bad = deepcopy(good)
        bad[0]['foo'] = 0
        schema_fail(bad)
        bad = deepcopy(good)
        bad[0]['available_answers'][0]['foo'] = 0
        schema_fail(bad)
        bad = deepcopy(good)
        bad[0]['available_answers'][0]['chosen'] = True
        value_fail(bad)
        bad = deepcopy(good)
        bad[0]['available_answers'][1]['chosen'] = False
        value_fail(bad)
        bad = deepcopy(good)
        bad[0]['available_answers'][1]['answer_text'] = '0'
        value_fail(bad)
        bad = deepcopy(good)
        bad += [deepcopy(bad[0])]
        value_fail(bad)

    def test_match(self):

        def answers(presets):
            answers = AnswersList([])
            for a in presets:
                answers.question_answer_complexes += [{
                    'question': a[0],
                    'choice': a[1],
                    'acceptable_choices': a[2],
                    'importance': a[3],
                }]
            return answers

        q1 = MultiChoiceQuestion('x', ('0', '1', '2'))
        q2 = MultiChoiceQuestion('x', ('0', '1'))
        q3 = MultiChoiceQuestion('y', ('0', '1', '2'))
        a1 = (q1, 0, (0,), 100)
        a2 = (q2, 0, (0,), 100)
        a3 = (q3, 0, (0,), 100)
        self.assertEqual(match(answers([]), answers([])), 0)
        self.assertEqual(match(answers([a1]), answers([])), 0)
        self.assertEqual(match(answers([a1]), answers([a1])), 0)
        self.assertEqual(match(answers([a1, a2]), answers([a1])), 0)
        self.assertEqual(match(answers([a1, a2]), answers([a1, a2])), 0.5)
        self.assertEqual(match(answers([a1, a2, a3]), answers([a1, a2, a3])),
                         0.6666666666666667)
        self.assertEqual(match(answers([a1, a2, a3]), answers([a1, a2])), 0.5)
        a1 = (q1, 0, (1, 2), 50)
        b1 = (q1, 1, (1,), 25)
        a2 = (q2, 0, (0,), 10)
        b2 = (q2, 1, (0,), 10)
        a3 = (q3, 0, (0,), 50)
        b3 = (q3, 1, (0,), 70)
        self.assertEqual(match(answers([a1, a2]), answers([b1, b2])), 0)
        self.assertEqual(match(answers([a1, a2, a3]), answers([b1, b2, b3])),
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
            if answer_1['question'] == answer_2['question']:
                shared_questions += 1
                answers_1_maxpoints += answer_1['importance']
                answers_2_maxpoints += answer_2['importance']
                if answer_1['choice'] in answer_2['acceptable_choices']:
                    answers_2_points += answer_2['importance']
                if answer_2['choice'] in answer_1['acceptable_choices']:
                    answers_1_points += answer_1['importance']
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
    import sys
    import os.path
    import json
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
            d = json.loads(json_text)
        except json.decoder.JSONDecodeError as err:
            print('Trouble JSON-decoding answers file:', err)
            exit(1)
        try:
            answers_lists += [AnswersList(d)]
        except (ValueError, jsonschema.exceptions.ValidationError) as err:
            print('Malformed answers file:', err)
            exit(1)
    print(match(answers_lists[0], answers_lists[1]))
