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
    argparser.add_argument('-t', '--target', metavar='FILEPATH',
                           help='answered questions file to write/append')
    argparser.add_argument('-s', '--source', metavar='FILEPATH',
                           help='answered questions file to source new ' +
                                'questions from')
    argparser.add_argument('-g', '--get', action='store_true',
                           help='treat FILEPATH for --source as URL to '
                                'retrieve data remotely from')
    args = argparser.parse_args()
    aq_lists = [matchlib.AnsweredQuestionsList(),
                matchlib.AnsweredQuestionsList()]
    paths = []
    if args.target:
        paths += [args.target]
    if args.source:
        paths += [args.source]
    for i in range(len(paths)):
        path = paths[i]
        if args.get and i == 1:
            try:
                path, _ = urllib.request.urlretrieve(path)
            except (ValueError, urllib.error.HTTPError) as err:
                print('trouble retrieving file:', err)
                exit(1)
        if os.path.isfile(path):
            try:
                aq_list = matchlib.AnsweredQuestionsList(path=path)
            except matchlib.AnsweredQuestionsParseError as err:
                print(err)
                exit(1)
            aq_lists[i] = aq_list
    aq_list = aq_lists[0]
    if args.source:
        questions_template = aq_lists[1]
        questions = [a.question for a
                     in sorted(questions_template.db,
                               key=lambda aq: aq.importance, reverse=True)
                     if a.question not in aq_list.unique_questions]
        for q in questions:
            print('QUESTION: ' + q.prompt)
            for i in range(len(q.selectables)):
                print('#%s: %s' % (str(i), q.selectables[i]))
            i_max = i
            if affirm('Answer this question?'):
                acceptable = []
                choice = get_int('your answer?', i_max)
                importance = get_int('importance?')
                if importance > 0:
                    for i in range(len(q.selectables)):
                        if affirm('acceptable choice of your ideal match? ' +
                                  q.selectables[i]):
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
        more_aqs = True
        i_aqs = -1
        while more_aqs:
            i_aqs += 1
            while True:
                selectable = get_string('selectable #' + str(i_aqs) + ': ')
                if selectable not in selectables:
                    break
                print('duplicate selectable, please try again')
            selectables += [selectable]
            if affirm('an acceptable choice of your ideal match?'):
                acceptable_choices += [i_aqs]
            if len(selectables) < 2:
                continue
            if not affirm('add another selectable?'):
                more_aqs = False
        question = matchlib.MultiChoiceQuestion(prompt, selectables)
        importance = get_int('how important is your ideal match\'s choice to '
                             'you?')
        choice = get_int('your own choice of answer? ', i_aqs)
        aq = matchlib.AnsweredQuestion(question, choice, acceptable_choices,
                                       importance)
        try:
            aq_list.add(aq)
        except matchlib.QuestionDuplicationError:
            if affirm('question already answered, overwrite old answer?'):
                aq_list.add(aq, True)
    json_dump = json.dumps(aq_list.to_json(), indent=2)
    if args.target:
        f = open(args.target, 'w')
        f.write(json_dump)
        f.close()
    else:
        print(json_dump)
