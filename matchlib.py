#!/usr/bin/env python3

import unittest
import jsonschema


schema = {
    '$schema': 'http://json-schema.org/schema#',
    'type': 'array',
    'items': {
        'type': 'object',
        'properties': {
            'prompt': {
                'type': 'string',
                'minLength': 1
            },
            'selectables': {
                'type': 'array',
                'items': {
                    'type': 'object',
                    'properties': {
                        'text': {
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
                    'required': ['text'],
                    'additionalProperties': False
                },
                'minItems': 2
            },
            'importance': {
                'type': 'integer',
                'minimum': 0
            }
        },
        'required': ['prompt', 'selectables', 'importance'],
        'additionalProperties': False
    }
}


class AnsweredQuestionsParseError(ValueError):
    pass


class QuestionDuplicationError(ValueError):
    pass


class MultiChoiceQuestion:

    def __init__(self, prompt, selectables):
        unique_selectables = []
        for selectable in selectables:
            if selectable in unique_selectables:
                raise ValueError('duplicate selectable: ' + selectable)
            unique_selectables += [selectable]
        self.prompt = prompt
        self.selectables = selectables

    def __eq__(self, other):
        if type(other) != MultiChoiceQuestion:
            msg = 'can compare MultiChoiceQuestion only with same type'
            raise TypeError(msg)
        return self.prompt == other.prompt and \
            self.selectables == other.selectables


class AnsweredQuestion:

    def __init__(self, question, choice, acceptable, importance):
        self.question = question
        self.choice = choice
        self.acceptable = acceptable
        self.importance = importance


class AnsweredQuestionsList:

    def __init__(self, json_dict=[], aqs=[], path=None):
        self.db = []
        self.unique_questions = []
        for aq in aqs:
            self.add(aq)
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
            msg = 'Trouble JSON-decoding answered questions file: ' + str(err)
            raise AnsweredQuestionsParseError(msg)
        try:
            self.add_json(d)
        except (ValueError, jsonschema.exceptions.ValidationError) as err:
            msg = 'Malformed answered questions file: ' + str(err)
            raise AnsweredQuestionsParseError(msg)

    def add_json(self, json):
        jsonschema.validate(json, schema)
        for aq in json:
            selectables = []
            choice = -1
            acceptable = []
            for i in range(len(aq['selectables'])):
                selectable = aq['selectables'][i]
                selectables += [selectable['text']]
                if 'chosen' in selectable and selectable['chosen']:
                    if choice > -1:
                        raise ValueError('more than one selectable chosen')
                    choice = i
                if 'acceptable' in selectable and \
                        selectable['acceptable']:
                    acceptable += [i]
            if choice == -1:
                raise ValueError('no selectable chosen')
            question = MultiChoiceQuestion(aq['prompt'], selectables)
            prepared = AnsweredQuestion(question, choice, acceptable,
                                        aq['importance'])
            self.add(prepared)

    def add(self, aq, overwrite=False):
        if aq.question in self.unique_questions:
            if overwrite:
                i = self.unique_questions.index(aq.question)
                self.db[i] = aq
                return
            else:
                raise QuestionDuplicationError
        self.unique_questions += [aq.question]
        self.db += [aq]

    def to_json(self):
        aq_json = []
        for entry in self.db:
            d = {
                'prompt': entry.question.prompt,
                'selectables': [],
                'importance': entry.importance,
            }
            for i in range(len(entry.question.selectables)):
                selectable = {
                    'text': entry.question.selectables[i]
                }
                if i == entry.choice:
                    selectable['chosen'] = True
                if i in entry.acceptable:
                    selectable['acceptable'] = True
                d['selectables'] += [selectable]
            aq_json += [d]
        return aq_json


class TestAll(unittest.TestCase):

    def test_answered_questions_list(self):
        from functools import partial
        from copy import deepcopy
        schema_fail = partial(self.assertRaises,
                              jsonschema.exceptions.ValidationError,
                              AnsweredQuestionsList)
        value_fail = partial(self.assertRaises, ValueError,
                             AnsweredQuestionsList)
        schema_fail({})
        AnsweredQuestionsList([])
        schema_fail([{}])
        schema_fail([0])
        good = [{
          "prompt": "?",
          "selectables": [{
            "text": "0",
            "chosen": False,
            "acceptable": True
            }, {
            "text": "1",
            "chosen": True,
            "acceptable": True
          }],
          "importance": 0
        }]
        AnsweredQuestionsList(good)

        # test JSON schema constraints
        bad = deepcopy(good)
        del bad[0]['selectables'][0]
        schema_fail(bad)
        bad = deepcopy(good)
        bad[0]['prompt'] = 0
        schema_fail(bad)
        bad[0]['prompt'] = ''
        schema_fail(bad)
        del bad[0]['prompt']
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
        bad[0]['selectables'][0]['text'] = 0
        schema_fail(bad)
        bad[0]['selectables'][0]['text'] = ''
        schema_fail(bad)
        del bad[0]['selectables'][0]['text']
        schema_fail(bad)
        bad = deepcopy(good)
        bad[0]['selectables'][0]['chosen'] = 'x'
        schema_fail(bad)
        bad = deepcopy(good)
        bad[0]['selectables'][0]['acceptable'] = 'x'
        schema_fail(bad)
        bad[0]['selectables'][0] = 'x'
        schema_fail(bad)
        bad = deepcopy(good)
        bad[0]['foo'] = 0
        schema_fail(bad)
        bad = deepcopy(good)
        bad[0]['selectables'][0]['foo'] = 0
        schema_fail(bad)

        # test extra-schema uniqueness constraints
        bad = deepcopy(good)
        bad[0]['selectables'][0]['chosen'] = True
        value_fail(bad)
        bad = deepcopy(good)
        bad[0]['selectables'][1]['chosen'] = False
        value_fail(bad)
        bad = deepcopy(good)
        bad[0]['selectables'][1]['text'] = '0'
        value_fail(bad)
        bad = deepcopy(good)
        bad += [deepcopy(bad[0])]
        self.assertRaises(QuestionDuplicationError, AnsweredQuestionsList, bad)

        # test input JSON == output JSON
        good2 = deepcopy(good)
        del good2[0]['selectables'][0]['chosen']
        good2 += [deepcopy(good2[0])]
        good2[1]['prompt'] += '?'
        a = AnsweredQuestionsList(good2)
        self.assertEqual(a.to_json(), good2)

        # test overwrite
        alt_aq = deepcopy(a.db[1])
        alt_aq .choice = 0
        good_cmp = deepcopy(good2)
        good_cmp[1]['selectables'][0]['chosen'] = True
        good_cmp[1]['selectables'][1]['chosen'] = False
        self.assertRaises(QuestionDuplicationError, a.add, alt_aq)
        a.add(alt_aq, True)
        self.assertEqual(a.to_json(),
                         AnsweredQuestionsList(good_cmp).to_json())
