#!/bin/bash
source ../../../main/colors.sh

rendu_file="../../../../rendu/merge_and_sort_desc/merge_and_sort_desc.py"

if [ ! -f "$rendu_file" ]; then
    echo "$(tput setaf 1)$(tput bold)FAIL: Missing file merge_and_sort_desc.py$(tput sgr 0)"
    exit 1
fi

cat > /tmp/test_merge_and_sort_desc.py << 'EOF'
import sys
sys.path.insert(0, sys.argv[1])
from merge_and_sort_desc import merge_and_sort_desc

tests = [
    ([1, 3, 5], [2, 4, 6], [6, 5, 4, 3, 2, 1]),
    ([10, 2], [3, 7, 2], [10, 7, 3, 2, 2]),
    ([], [1, 2, 3], [3, 2, 1]),
    ([], [], []),
    ([5], [5], [5, 5]),
    ([100, -1, 50], [0, 200], [200, 100, 50, 0, -1]),
    ([1], [], [1]),
]

failed = False
for l1, l2, expected in tests:
    # Check original lists are not modified
    l1_copy = l1[:]
    l2_copy = l2[:]
    result = merge_and_sort_desc(l1, l2)
    if result != expected:
        print(f"FAIL: merge_and_sort_desc({l1_copy}, {l2_copy}) = {result}, expected {expected}")
        failed = True
    if l1 != l1_copy or l2 != l2_copy:
        print(f"FAIL: Original lists were modified!")
        failed = True

if failed:
    sys.exit(1)
else:
    sys.exit(0)
EOF

python3 /tmp/test_merge_and_sort_desc.py "../../../../rendu/merge_and_sort_desc"
if [ $? -ne 0 ]; then
    echo "$(tput setaf 1)$(tput bold)FAIL$(tput sgr 0)"
    rm -f /tmp/test_merge_and_sort_desc.py
    exit 1
fi

rm -f /tmp/test_merge_and_sort_desc.py
echo "$(tput setaf 2)$(tput bold)PASSED 🎉$(tput sgr 0)"
exit 0
