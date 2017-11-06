multichoice_questions_matcher
=============================

Setup
-----

You need to install the requirements from the requirements.txt file:

 $ pip install -r requirements.txt

Basic usage
-----------

Create and answer questions, write json to stdout:

  $ ./answer.py

Create and answer questions, write json to FILE (appends if file pre-existing):

  $ ./answer.py --target FILE

Answer questions from json in FILE_OLD (may be a local filesystem path or a
URL to a remote location), write answers to FILE_NEW:

  $ ./answer.py --target FILE_NEW --source FILE_OLD

Compare/analyze matching questions/answers from FILE_1, FILE_2 (may be local
filesystem paths or URLs to remote locations):

  $ ./matcher.py FILE_1 FILE_2