#!/usr/bin/env python3

import matchlib


def get_string(prompt):
    string = input(prompt)
    while len(string) < 1:
        string = input('string too short, retry: ')
    return string


def get_int(prompt, maximum=None):
    str_limit = '…'
    if maximum:
        str_limit = str(maximum)
    prompt = prompt + ' (0-' + str_limit + '): '
    string = input(prompt)
    while True:
        if not string.isdigit():
            string = input("please enter only digits: ")
            continue
        i = int(string)
        if maximum and i > maximum:
            string = input("value must be <= " + str(maximum) + ': ')
            continue
        return i


def affirm(prompt):
    string = input(prompt + ' (y/n): ')
    while string not in {'y', 'n'}:
        string = input('answer must be either "y" or "n": ')
    return string == 'y'


if __name__ == '__main__':
    import argparse
    import os.path
    import json
    import urllib
    argparser = argparse.ArgumentParser()
    argparser.add_argument('-t', '--target', metavar='PATH',
                           help='answered questions file to write/append')
    argparser.add_argument('-s', '--source', metavar='PATH',
                           help='answered questions file to source new '
                                'questions from; may be local file path or '
                                'URL')
    args = argparser.parse_args()
    aq_list = matchlib.AnsweredQuestionsList()
    if args.target:
        if os.path.isfile(args.target):
            try:
                aq_list = matchlib.AnsweredQuestionsList(path=args.target)
            except matchlib.AnsweredQuestionsParseError as err:
                print(err)
                exit(1)
    if args.source:
        path = args.source
        if urllib.parse.urlparse(path).scheme != '':
            try:
                path, _ = urllib.request.urlretrieve(path)
            except (ValueError, urllib.error.HTTPError) as err:
                print('trouble retrieving file:', err)
                exit(1)
        if not os.path.isfile(path):
            print('source file not found:', path)
            exit(1)
        try:
            questions_template = matchlib.AnsweredQuestionsList(path=path)
        except matchlib.AnsweredQuestionsParseError as err:
            print(err)
            exit(1)
        questions = [a.question for a
                     in sorted(questions_template.db,
                               key=lambda aq: aq.importance, reverse=True)
                     if a.question not in aq_list.unique_questions]
        for q in questions:
            print('QUESTION: ' + q.prompt)
            for i, selectable in enumerate(q.selectables):
                print('#%s: %s' % (str(i), selectable))
            i_max = i
            if affirm('Answer this question?'):
                acceptable = []
                choice = get_int('your answer?', i_max)
                importance = get_int('importance?')
                if importance > 0:
                    for i, selectable in enumerate(q.selectables):
                        if affirm('acceptable choice of your ideal match? ' +
                                  selectable):
                            acceptable += [i]
                aq = matchlib.AnsweredQuestion(q, choice, acceptable,
                                               importance)
                aq_list.add(aq)
    while True:
        if not affirm('add another answered question?'):
            break
        prompt = get_string('question prompt: ')
        selectables = []
        acceptable_choices = []
        more_selectables = True
        i_selectables = -1
        while more_selectables:
            i_selectables += 1
            while True:
                selectable = get_string('selectable #%s: ' % i_selectables)
                if selectable not in selectables:
                    break
                print('duplicate selectable, please try again')
            selectables += [selectable]
            if affirm('an acceptable choice of your ideal match?'):
                acceptable_choices += [i_selectables]
            if len(selectables) < 2:
                continue
            if not affirm('add another selectable?'):
                more_selectables = False
        question = matchlib.MultiChoiceQuestion(prompt, selectables)
        importance = get_int('how important is your ideal match\'s choice to '
                             'you?')
        choice = get_int('your own choice of answer? ', i_selectables)
        aq = matchlib.AnsweredQuestion(question, choice, acceptable_choices,
                                       importance)
        try:
            aq_list.add(aq)
        except matchlib.QuestionDuplicationError:
            if affirm('question already answered, overwrite old answer?'):
                aq_list.add(aq, True)
    json_dump = json.dumps(aq_list.to_json(), indent=2, sort_keys=True)
    if args.target:
        with open(args.target, 'w') as f:
            f.write(json_dump)
    else:
        print(json_dump)
