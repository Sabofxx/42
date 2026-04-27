#!/bin/bash
source ../../../main/colors.sh

rendu_file="../../../../rendu/convert_base/convert_base.py"

if [ ! -f "$rendu_file" ]; then
    echo "$(tput setaf 1)$(tput bold)FAIL: Missing file convert_base.py$(tput sgr 0)"
    exit 1
fi

cat > /tmp/test_convert_base.py << 'EOF'
import sys
import io
sys.path.insert(0, sys.argv[1])
from convert_base import convert_base

tests = [
    (("ff", 16, 2), "11111111"),
    (("10", 2, 10), "2"),
    (("z", 36, 10), "35"),
    (("1g", 16, 10), "ERROR"),
    (("0", 10, 2), "0"),
    (("10", 10, 16), "A"),
    (("255", 10, 16), "FF"),
    (("111", 2, 10), "7"),
    (("abc", 10, 2), "ERROR"),
]

failed = False
for args, expected in tests:
    # Capture stdout
    old_stdout = sys.stdout
    sys.stdout = io.StringIO()
    convert_base(*args)
    output = sys.stdout.getvalue().strip()
    sys.stdout = old_stdout

    if output.upper() != expected.upper():
        print(f"FAIL: convert_base{args} printed \"{output}\", expected \"{expected}\"")
        failed = True

if failed:
    sys.exit(1)
else:
    sys.exit(0)
EOF

python3 /tmp/test_convert_base.py "../../../../rendu/convert_base"
if [ $? -ne 0 ]; then
    echo "$(tput setaf 1)$(tput bold)FAIL$(tput sgr 0)"
    rm -f /tmp/test_convert_base.py
    exit 1
fi

rm -f /tmp/test_convert_base.py
echo "$(tput setaf 2)$(tput bold)PASSED 🎉$(tput sgr 0)"
exit 0
