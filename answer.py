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
    if len(sys.argv) not in {2, 3}:
        print('need one or two filename arguments')
        exit(1)
    paths = [sys.argv[1]]
    if len(sys.argv) == 3:
        paths += [sys.argv[2]]
    answers_lists = []
    for path in paths:
        if os.path.isfile(path):
            try:
                answers_list = matchlib.AnswersList(path=path)
            except matchlib.AnswersParseError as err:
                print(err)
                exit(1)
        answers_lists += [answers_list]
    if len(answers_lists) == 0:
        answers_lists = [matchlib.AnswersList()]
    answers_list = answers_lists[0]
    if len(answers_lists) == 2:
        questions_template = answers_lists[1]
        questions = [a.question for a
                     in questions_template.question_answer_complexes
                     if not a.question in answers_list.unique_questions]
        for q in questions:
            print('QUESTION: ' + q.prompt)
            for i in range(len(q.answers)):
                print('#%s: %s' % (str(i), q.answers[i]))
            i_max = i
            if affirm('Answer this question?'):
                acceptable_choices = []
                choice = get_int('your answer?', i_max)
                importance = get_int('importance?')
                if importance > 0:
                    for i in range(len(q.answers)):
                        if affirm('acceptable answer? ' + q.answers[i]):
                            acceptable_choices += [i]
                a = matchlib.Answer(q, choice, acceptable_choices, importance)
                answers_list.add_answer(a)
    while True:
        if not affirm('add another question+answer?'):
            break
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
    f = open(paths[0], 'w')
    f.write(json.dumps(answers_list.to_json(), indent=2))
    f.close()
