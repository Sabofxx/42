#!/bin/bash
source ../../../main/colors.sh

rendu_file="../../../../rendu/valid_palindrome/valid_palindrome.py"

if [ ! -f "$rendu_file" ]; then
    echo "$(tput setaf 1)$(tput bold)FAIL: Missing file valid_palindrome.py$(tput sgr 0)"
    exit 1
fi

cat > /tmp/test_valid_palindrome.py << 'EOF'
import sys
sys.path.insert(0, sys.argv[1])
from valid_palindrome import valid_palindrome

tests = [
    ("Was it a car or a cat I saw?", True),
    ("tab a cat", False),
    ("A man, a plan, a canal: Panama", True),
    ("No lemon, no melon", True),
    ("", True),
    ("a", True),
    ("race a car", False),
    ("12321", True),
    ("123 21", False),
    ("Madam", True),
]

failed = False
for s, expected in tests:
    result = valid_palindrome(s)
    if result != expected:
        print(f"FAIL: valid_palindrome(\"{s}\") = {result}, expected {expected}")
        failed = True

if failed:
    sys.exit(1)
else:
    sys.exit(0)
EOF

python3 /tmp/test_valid_palindrome.py "../../../../rendu/valid_palindrome"
if [ $? -ne 0 ]; then
    echo "$(tput setaf 1)$(tput bold)FAIL$(tput sgr 0)"
    rm -f /tmp/test_valid_palindrome.py
    exit 1
fi

rm -f /tmp/test_valid_palindrome.py
echo "$(tput setaf 2)$(tput bold)PASSED 🎉$(tput sgr 0)"
exit 0
