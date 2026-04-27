#!/bin/bash
source ../../../main/colors.sh

rendu_file="../../../../rendu/valid_anagram/valid_anagram.py"

if [ ! -f "$rendu_file" ]; then
    echo "$(tput setaf 1)$(tput bold)FAIL: Missing file valid_anagram.py$(tput sgr 0)"
    exit 1
fi

cat > /tmp/test_valid_anagram.py << 'EOF'
import sys
sys.path.insert(0, sys.argv[1])
from valid_anagram import valid_anagram

tests = [
    ("racecar", "carrace", True),
    ("jar", "jam", False),
    ("listen", "silent", True),
    ("aabbcc", "abcabc", True),
    ("abc", "ab", False),
    ("", "", True),
    ("a", "a", True),
    ("a", "b", False),
    ("anagram", "nagaram", True),
    ("rat", "car", False),
]

failed = False
for s, t, expected in tests:
    result = valid_anagram(s, t)
    if result != expected:
        print(f"FAIL: valid_anagram(\"{s}\", \"{t}\") = {result}, expected {expected}")
        failed = True

if failed:
    sys.exit(1)
else:
    sys.exit(0)
EOF

python3 /tmp/test_valid_anagram.py "../../../../rendu/valid_anagram"
if [ $? -ne 0 ]; then
    echo "$(tput setaf 1)$(tput bold)FAIL$(tput sgr 0)"
    rm -f /tmp/test_valid_anagram.py
    exit 1
fi

rm -f /tmp/test_valid_anagram.py
echo "$(tput setaf 2)$(tput bold)PASSED 🎉$(tput sgr 0)"
exit 0
