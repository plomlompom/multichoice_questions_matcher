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

Answer questions from json in FILE_OLD, write answers to FILE_NEW:

  $ ./answer.py --target FILE_NEW --source FILE_OLD

Compare/analyze matching questions/answers from FILE_1, FILE_2:

  $ ./matcher.py FILE_1 FILE_2

Matching and question-sourcing files from the web
-------------------------------------------------

Both the answer.py and the matcher.py application may use remote files from the
web instead of local files. To source questions from a remote web location, use
the `-g`/`--get` option.

The answer.py application expects no arguments to `-g`, as it can meaningfully
apply it only to the source file path:

  $ ./answer.py --target FILE_NEW --source URL --get

The matcher.py application expects two file paths, and therefore we need to
specify with path to treat as a URL by naming its index:

  $ ./matcher.py FILE_1 FILE_2 -g0

We may also match two files that are both located remotely:

  $ ./matcher.py FILE_1 FILE_2 -g0 -g1