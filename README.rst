multichoice_questions_matcher
=============================

Create and answer questions, write json to stdout:

 $ ./answer.py

Create and answer questions, write json to FILE (appends if file pre-existing):

 $ ./answer.py --target FILE

Answer questions from json in FILE_OLD, write answers to FILE_NEW:

 $ ./answer.py --target FILE_NEW --source FILE_OLD

Compare/analyze matching questions/answers from FILE_1, FILE_2:

 $ ./matcher.py FILE_1 FILE_2