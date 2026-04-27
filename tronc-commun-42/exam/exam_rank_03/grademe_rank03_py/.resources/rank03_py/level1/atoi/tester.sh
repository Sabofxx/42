#!/bin/bash
source ../../../main/colors.sh

rendu_file="../../../../rendu/atoi/atoi.py"

if [ ! -f "$rendu_file" ]; then
    echo "$(tput setaf 1)$(tput bold)FAIL: Missing file atoi.py$(tput sgr 0)"
    exit 1
fi

# Create test script
cat > /tmp/test_atoi.py << 'EOF'
import sys
sys.path.insert(0, sys.argv[1])
from atoi import atoi

tests = [
    ("42", 42),
    ("  -42abc", -42),
    ("+123", 123),
    ("abc", 0),
    ("   +0", 0),
    ("-0", 0),
    ("  123abc456", 123),
    ("", 0),
    ("   ", 0),
    ("--5", 0),
    ("2147483647", 2147483647),
    ("-2147483648", -2147483648),
]

failed = False
for s, expected in tests:
    result = atoi(s)
    if result != expected:
        print(f"FAIL: atoi(\"{s}\") = {result}, expected {expected}")
        failed = True

if failed:
    sys.exit(1)
else:
    sys.exit(0)
EOF

python3 /tmp/test_atoi.py "../../../../rendu/atoi"
if [ $? -ne 0 ]; then
    echo "$(tput setaf 1)$(tput bold)FAIL$(tput sgr 0)"
    rm -f /tmp/test_atoi.py
    exit 1
fi

rm -f /tmp/test_atoi.py
echo "$(tput setaf 2)$(tput bold)PASSED 🎉$(tput sgr 0)"
exit 0
