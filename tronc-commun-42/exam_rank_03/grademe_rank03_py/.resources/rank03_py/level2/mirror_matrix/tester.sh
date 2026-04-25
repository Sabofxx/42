#!/bin/bash
source ../../../main/colors.sh

rendu_file="../../../../rendu/mirror_matrix/mirror_matrix.py"

if [ ! -f "$rendu_file" ]; then
    echo "$(tput setaf 1)$(tput bold)FAIL: Missing file mirror_matrix.py$(tput sgr 0)"
    exit 1
fi

cat > /tmp/test_mirror_matrix.py << 'EOF'
import sys
sys.path.insert(0, sys.argv[1])
from mirror_matrix import mirror_matrix

tests = [
    ([[1, 2, 3], [4, 5, 6], [7, 8, 9]],
     [[3, 2, 1], [6, 5, 4], [9, 8, 7]]),
    ([[1, 2], [3, 4]],
     [[2, 1], [4, 3]]),
    ([[1]], [[1]]),
    ([], []),
    ([[1, 2, 3, 4]], [[4, 3, 2, 1]]),
]

failed = False
for matrix, expected in tests:
    original = [row[:] for row in matrix]
    result = mirror_matrix(matrix)
    if result != expected:
        print(f"FAIL: mirror_matrix({original}) = {result}, expected {expected}")
        failed = True
    if matrix != original:
        print(f"FAIL: Original matrix was modified!")
        failed = True

if failed:
    sys.exit(1)
else:
    sys.exit(0)
EOF

python3 /tmp/test_mirror_matrix.py "../../../../rendu/mirror_matrix"
if [ $? -ne 0 ]; then
    echo "$(tput setaf 1)$(tput bold)FAIL$(tput sgr 0)"
    rm -f /tmp/test_mirror_matrix.py
    exit 1
fi

rm -f /tmp/test_mirror_matrix.py
echo "$(tput setaf 2)$(tput bold)PASSED 🎉$(tput sgr 0)"
exit 0
