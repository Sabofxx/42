#!/bin/bash
source ../../../main/colors.sh

rendu_file="../../../../rendu/mirror_matrix_vertical/mirror_matrix_vertical.py"

if [ ! -f "$rendu_file" ]; then
    echo "$(tput setaf 1)$(tput bold)FAIL: Missing file mirror_matrix_vertical.py$(tput sgr 0)"
    exit 1
fi

cat > /tmp/test_mirror_matrix_vertical.py << 'EOF'
import sys
sys.path.insert(0, sys.argv[1])
from mirror_matrix_vertical import mirror_matrix_vertical

tests = [
    ([[1, 2, 3], [4, 5, 6], [7, 8, 9]],
     [[7, 8, 9], [4, 5, 6], [1, 2, 3]]),
    ([[1, 2], [3, 4]],
     [[3, 4], [1, 2]]),
    ([[1]], [[1]]),
    ([], []),
    ([[1, 2], [3, 4], [5, 6], [7, 8]],
     [[7, 8], [5, 6], [3, 4], [1, 2]]),
]

failed = False
for matrix, expected in tests:
    original = [row[:] for row in matrix]
    result = mirror_matrix_vertical(matrix)
    if result != expected:
        print(f"FAIL: mirror_matrix_vertical({original}) = {result}, expected {expected}")
        failed = True
    if matrix != original:
        print(f"FAIL: Original matrix was modified!")
        failed = True

if failed:
    sys.exit(1)
else:
    sys.exit(0)
EOF

python3 /tmp/test_mirror_matrix_vertical.py "../../../../rendu/mirror_matrix_vertical"
if [ $? -ne 0 ]; then
    echo "$(tput setaf 1)$(tput bold)FAIL$(tput sgr 0)"
    rm -f /tmp/test_mirror_matrix_vertical.py
    exit 1
fi

rm -f /tmp/test_mirror_matrix_vertical.py
echo "$(tput setaf 2)$(tput bold)PASSED 🎉$(tput sgr 0)"
exit 0
