#!/bin/bash
source ../../../main/colors.sh

rendu_file="../../../../rendu/capitalize_words/capitalize_words.py"

if [ ! -f "$rendu_file" ]; then
    echo "$(tput setaf 1)$(tput bold)FAIL: Missing file capitalize_words.py$(tput sgr 0)"
    exit 1
fi

cat > /tmp/test_capitalize_words.py << 'EOF'
import sys
sys.path.insert(0, sys.argv[1])
from capitalize_words import capitalize_words

tests = [
    ("hello world", "Hello World"),
    ("42 madrid exam", "42 Madrid Exam"),
    ("  multiple   spaces ", "  Multiple   Spaces "),
    ("mixed CASE letters", "Mixed Case Letters"),
    ("", ""),
    ("a", "A"),
    ("already Capital", "Already Capital"),
    ("ALL UPPER CASE", "All Upper Case"),
]

failed = False
for s, expected in tests:
    result = capitalize_words(s)
    if result != expected:
        print(f"FAIL: capitalize_words(\"{s}\") = \"{result}\", expected \"{expected}\"")
        failed = True

if failed:
    sys.exit(1)
else:
    sys.exit(0)
EOF

python3 /tmp/test_capitalize_words.py "../../../../rendu/capitalize_words"
if [ $? -ne 0 ]; then
    echo "$(tput setaf 1)$(tput bold)FAIL$(tput sgr 0)"
    rm -f /tmp/test_capitalize_words.py
    exit 1
fi

rm -f /tmp/test_capitalize_words.py
echo "$(tput setaf 2)$(tput bold)PASSED 🎉$(tput sgr 0)"
exit 0
