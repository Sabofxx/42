#!/bin/bash
source ../../../main/colors.sh

rendu_file="../../../../rendu/brackets/brackets.py"

if [ ! -f "$rendu_file" ]; then
    echo "$(tput setaf 1)$(tput bold)FAIL: Missing file brackets.py$(tput sgr 0)"
    exit 1
fi

cat > /tmp/test_brackets.py << 'EOF'
import sys
sys.path.insert(0, sys.argv[1])
from brackets import brackets

tests = [
    ("()", True),
    ("([{}])", True),
    ("(]", False),
    ("([)", False),
    ("a(b[c]d)", True),
    ("[{adaudna}]", True),
    ("[{adaudna}])", False),
    ("abc{[123(xyz)]}", True),
    ("", True),
    ("((()))", True),
    ("((())", False),
    ("{[()]}", True),
    ("}{", False),
    ("hello world", True),
    ("(((((", False),
    (")))))", False),
]

failed = False
for s, expected in tests:
    result = brackets(s)
    if result != expected:
        print(f"FAIL: brackets(\"{s}\") = {result}, expected {expected}")
        failed = True

if failed:
    sys.exit(1)
else:
    sys.exit(0)
EOF

python3 /tmp/test_brackets.py "../../../../rendu/brackets"
if [ $? -ne 0 ]; then
    echo "$(tput setaf 1)$(tput bold)FAIL$(tput sgr 0)"
    rm -f /tmp/test_brackets.py
    exit 1
fi

rm -f /tmp/test_brackets.py
echo "$(tput setaf 2)$(tput bold)PASSED 🎉$(tput sgr 0)"
exit 0
