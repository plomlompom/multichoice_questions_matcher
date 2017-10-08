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
    import sys
    import os.path
    import json
    if len(sys.argv) != 2:
        print('need precisely one filename argument')
        exit(1)
    path = sys.argv[1]
    answers_list = matchlib.AnswersList()
    if os.path.isfile(path):
        try:
            answers_list = matchlib.AnswersList(path=path)
        except matchlib.AnswersParseError as err:
            print(err)
            exit(1)
    more_questions = True
    while more_questions:
        prompt = get_string('question prompt: ')
        available_answers = []
        acceptable_answers = []
        more_answers = True
        i_answers = -1 
        while more_answers:
            i_answers += 1
            while True:
                answer = get_string('answer #' + str(i_answers) + ': ')
                if answer not in available_answers:
                    break
                print('duplicate answer, please try again')
            available_answers += [answer]
            if affirm('an acceptable answer of your ideal match?'):
                acceptable_answers += [i_answers]
            if len(available_answers) < 2:
                continue
            if not affirm('add another answer?'):
                more_answers = False
        question = matchlib.MultiChoiceQuestion(prompt, available_answers)
        importance = get_int('how important is your ideal match\'s answer to '
                             'you?')
        choice = get_int('your own choice of answer? ', i_answers)
        answer = matchlib.Answer(question, choice, acceptable_answers,
                                 importance)
        try:
            answers_list.add_answer(answer)
        except matchlib.QuestionDuplicationError:
            if affirm('question already answered, overwrite old answer?'):
                answers_list.add_answer(answer, True)
        if not affirm('add another question+answer?'):
            more_questions = False
    import json
    f = open(path, 'w')
    f.write(json.dumps(answers_list.to_json(), indent=2))
    f.close()
