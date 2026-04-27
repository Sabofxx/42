#!/bin/bash
source ../../../main/colors.sh

rendu_file="../../../../rendu/alternate_case/alternate_case.py"

if [ ! -f "$rendu_file" ]; then
    echo "$(tput setaf 1)$(tput bold)FAIL: Missing file alternate_case.py$(tput sgr 0)"
    exit 1
fi

cat > /tmp/test_alternate_case.py << 'EOF'
import sys
sys.path.insert(0, sys.argv[1])
from alternate_case import alternate_case

tests = [
    ("hello world", "HeLlO WoRlD"),
    ("42madrid", "42MaDrId"),
    ("python3.9 rocks!", "PyThOn3.9 RoCkS!"),
    ("a!b?c", "A!b?C"),
    ("", ""),
    ("123", "123"),
    ("A", "A"),
    ("ab", "Ab"),
    ("HELLO", "HeLlO"),
]

failed = False
for s, expected in tests:
    result = alternate_case(s)
    if result != expected:
        print(f"FAIL: alternate_case(\"{s}\") = \"{result}\", expected \"{expected}\"")
        failed = True

if failed:
    sys.exit(1)
else:
    sys.exit(0)
EOF

python3 /tmp/test_alternate_case.py "../../../../rendu/alternate_case"
if [ $? -ne 0 ]; then
    echo "$(tput setaf 1)$(tput bold)FAIL$(tput sgr 0)"
    rm -f /tmp/test_alternate_case.py
    exit 1
fi

rm -f /tmp/test_alternate_case.py
echo "$(tput setaf 2)$(tput bold)PASSED 🎉$(tput sgr 0)"
exit 0
