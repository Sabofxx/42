#!/bin/bash
source ../../../main/colors.sh

rendu_file="../../../../rendu/sorted/sorted.py"

if [ ! -f "$rendu_file" ]; then
    echo "$(tput setaf 1)$(tput bold)FAIL: Missing file sorted.py$(tput sgr 0)"
    exit 1
fi

cat > /tmp/test_sorted.py << 'EOF'
import sys
sys.path.insert(0, sys.argv[1])
from sorted import sort_by_length, sort_by_grade_desc, sort_by_multi

failed = False

# Test sort_by_length
tests_length = [
    (["banana", "kiwi", "fig"], ["fig", "kiwi", "banana"]),
    (["a", "bb", "ccc", "dd"], ["a", "bb", "dd", "ccc"]),
    ([], []),
    (["same", "size", "word"], ["same", "size", "word"]),
]

for words, expected in tests_length:
    result = sort_by_length(words)
    if result != expected:
        print(f"FAIL: sort_by_length({words}) = {result}, expected {expected}")
        failed = True

# Test sort_by_grade_desc
tests_grade = [
    ([("Ana", 8.5), ("Luis", 6.0), ("Marta", 9.2)],
     [("Marta", 9.2), ("Ana", 8.5), ("Luis", 6.0)]),
    ([("A", 10.0)], [("A", 10.0)]),
    ([], []),
]

for students, expected in tests_grade:
    result = sort_by_grade_desc(students)
    if result != expected:
        print(f"FAIL: sort_by_grade_desc({students}) = {result}, expected {expected}")
        failed = True

# Test sort_by_multi
tests_multi = [
    ([("Ana", 20), ("Luis", 20), ("Marta", 18)],
     [("Marta", 18), ("Ana", 20), ("Luis", 20)]),
    ([("Z", 1), ("A", 1), ("M", 2)],
     [("A", 1), ("Z", 1), ("M", 2)]),
    ([], []),
]

for data, expected in tests_multi:
    result = sort_by_multi(data)
    if result != expected:
        print(f"FAIL: sort_by_multi({data}) = {result}, expected {expected}")
        failed = True

if failed:
    sys.exit(1)
else:
    sys.exit(0)
EOF

python3 /tmp/test_sorted.py "../../../../rendu/sorted"
if [ $? -ne 0 ]; then
    echo "$(tput setaf 1)$(tput bold)FAIL$(tput sgr 0)"
    rm -f /tmp/test_sorted.py
    exit 1
fi

rm -f /tmp/test_sorted.py
echo "$(tput setaf 2)$(tput bold)PASSED 🎉$(tput sgr 0)"
exit 0
