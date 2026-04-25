#!/bin/bash
source ../../../main/colors.sh

rendu_file="../../../../rendu/whisper_lipher/whisper_lipher.py"

if [ ! -f "$rendu_file" ]; then
    echo "$(tput setaf 1)$(tput bold)FAIL: Missing file whisper_lipher.py$(tput sgr 0)"
    exit 1
fi

cat > /tmp/test_whisper_lipher.py << 'EOF'
import sys
sys.path.insert(0, sys.argv[1])
from whisper_lipher import whisper_lipher

tests = [
    ("Hello, World!", 3, "Khoor, Zruog!"),
    ("abc", 1, "bcd"),
    ("xyz", 2, "zab"),
    ("ABC", 26, "ABC"),
    ("", 5, ""),
    ("123!@#", 10, "123!@#"),
    ("Zoo", 1, "App"),
    ("aBcDe", 2, "cDeFg"),
    ("Hello", 0, "Hello"),
    ("abcdefghijklmnopqrstuvwxyz", 13, "nopqrstuvwxyzabcdefghijklm"),
]

failed = False
for text, shift, expected in tests:
    result = whisper_lipher(text, shift)
    if result != expected:
        print(f"FAIL: whisper_lipher(\"{text}\", {shift}) = \"{result}\", expected \"{expected}\"")
        failed = True

if failed:
    sys.exit(1)
else:
    sys.exit(0)
EOF

python3 /tmp/test_whisper_lipher.py "../../../../rendu/whisper_lipher"
if [ $? -ne 0 ]; then
    echo "$(tput setaf 1)$(tput bold)FAIL$(tput sgr 0)"
    rm -f /tmp/test_whisper_lipher.py
    exit 1
fi

rm -f /tmp/test_whisper_lipher.py
echo "$(tput setaf 2)$(tput bold)PASSED 🎉$(tput sgr 0)"
exit 0
