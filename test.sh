#!/bin/sh
set -e
set -x

python3 -m unittest *.py
./matcher.py tests/foo.json tests/bar.json > /tmp/matcher.py_test_output
diff /tmp/matcher.py_test_output tests/expected_matcher.py_test_output
cat tests/answer.py_input | ./answer.py > /tmp/answer.py_test_output
diff /tmp/answer.py_test_output tests/expected_answer.py_test_output

echo "TESTS SUCCEEDED."
