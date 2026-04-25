#!/bin/bash
source ../../../main/colors.sh

rendu_file="../../../../rendu/rotate_90/rotate_90.py"

if [ ! -f "$rendu_file" ]; then
    echo "$(tput setaf 1)$(tput bold)FAIL: Missing file rotate_90.py$(tput sgr 0)"
    exit 1
fi

cat > /tmp/test_rotate_90.py << 'EOF'
import sys
sys.path.insert(0, sys.argv[1])
from rotate_90 import rotate_90

tests = [
    ([[1, 2, 3], [4, 5, 6], [7, 8, 9]],
     [[7, 4, 1], [8, 5, 2], [9, 6, 3]]),
    ([[1, 2], [3, 4]],
     [[3, 1], [4, 2]]),
    ([[1]], [[1]]),
    ([[1, 2, 3, 4], [5, 6, 7, 8], [9, 10, 11, 12], [13, 14, 15, 16]],
     [[13, 9, 5, 1], [14, 10, 6, 2], [15, 11, 7, 3], [16, 12, 8, 4]]),
]

failed = False
for matrix, expected in tests:
    original = [row[:] for row in matrix]
    result = rotate_90(matrix)
    if result != expected:
        print(f"FAIL: rotate_90({original}) = {result}, expected {expected}")
        failed = True
    if matrix != original:
        print(f"FAIL: Original matrix was modified!")
        failed = True

if failed:
    sys.exit(1)
else:
    sys.exit(0)
EOF

python3 /tmp/test_rotate_90.py "../../../../rendu/rotate_90"
if [ $? -ne 0 ]; then
    echo "$(tput setaf 1)$(tput bold)FAIL$(tput sgr 0)"
    rm -f /tmp/test_rotate_90.py
    exit 1
fi

rm -f /tmp/test_rotate_90.py
echo "$(tput setaf 2)$(tput bold)PASSED 🎉$(tput sgr 0)"
exit 0
