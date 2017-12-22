multichoice_questions_matcher
=============================

Toolset for profiling oneself and one's matching desires by answering questions
and setting expectations for question answers from others. Questions, answers,
and answer expectations are stored in JSON files. Such files can be matched
against each other, producing a match percentage. Files may be exchanged by any
medium; they might be stored on the public web.

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

Some example profile files can be found in the ./tests/ directory.