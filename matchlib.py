#!/usr/bin/env python3

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
                    'type': 'object',
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


class AnswersParseError(ValueError):
    pass


class QuestionDuplicationError(ValueError):
    pass


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


class Answer:

    def __init__(self, question, choice, acceptable_choices, importance):
        self.question = question
        self.choice = choice
        self.acceptable_choices = acceptable_choices
        self.importance = importance


class AnswersList:

    def __init__(self, json_dict=[], answers=[], path=None):
        self.question_answer_complexes = []
        self.unique_questions = []
        for answer in answers:
            self.add_answer(answer)
        self.add_json(json_dict)
        if path:
            self.add_file(path)

    def add_file(self, path):
        import json
        f = open(path, 'r')
        json_text = f.read()
        f.close()
        try:
            d = json.loads(json_text)
        except json.decoder.JSONDecodeError as err:
            raise AnswersParseError('Trouble JSON-decoding answers file: '
                                    + str(err))
        try:
            self.add_json(d)
        except (ValueError, jsonschema.exceptions.ValidationError) as err:
            raise AnswersParseError('Malformed answers file: ' + str(err))

    def add_json(self, json):
        jsonschema.validate(json, schema)
        for answer in json:
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
            answer_prepared = Answer(question, choice, acceptable_choices,
                                     answer['importance'])
            self.add_answer(answer_prepared)

    def add_answer(self, answer, overwrite=False):
        if answer.question in self.unique_questions:
            if overwrite:
                i = self.unique_questions.index(answer.question)
                self.question_answer_complexes[i] = answer
                return
            else:
                raise QuestionDuplicationError
        self.unique_questions += [answer.question]
        self.question_answer_complexes += [answer]

    def to_json(self):
        answers_json = []
        for entry in self.question_answer_complexes:
            d = {
                'question_prompt': entry.question.prompt,
                'available_answers': [],
                'importance': entry.importance,
            }
            for i in range(len(entry.question.answers)):
                answer = {
                    'answer_text': entry.question.answers[i]
                }
                if i == entry.choice:
                    answer['chosen'] = True
                if i in entry.acceptable_choices:
                    answer['acceptable'] = True
                d['available_answers'] += [answer]
            answers_json += [d]
        return answers_json


class TestAll(unittest.TestCase):

    def test_answerlist(self):
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

        # test JSON schema constraints
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
        bad[0]['available_answers'][0] = 'x'
        schema_fail(bad)
        bad = deepcopy(good)
        bad[0]['foo'] = 0
        schema_fail(bad)
        bad = deepcopy(good)
        bad[0]['available_answers'][0]['foo'] = 0
        schema_fail(bad)

        # test extra-schema uniqueness constraints
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
        self.assertRaises(QuestionDuplicationError, AnswersList, bad)

        # test input JSON == output JSON
        good2 = deepcopy(good)
        del good2[0]['available_answers'][0]['chosen']
        good2 += [deepcopy(good2[0])]
        good2[1]['question_prompt'] += '?'
        a = AnswersList(good2)
        self.assertEqual(a.to_json(), good2)

        # test overwrite
        alt_answer = deepcopy(a.question_answer_complexes[1])
        alt_answer.choice = 0
        good_cmp = deepcopy(good2)
        good_cmp[1]['available_answers'][0]['chosen'] = True
        good_cmp[1]['available_answers'][1]['chosen'] = False
        self.assertRaises(QuestionDuplicationError, a.add_answer, alt_answer)
        a.add_answer(alt_answer, True)
        self.assertEqual(a.to_json(), AnswersList(good_cmp).to_json())
