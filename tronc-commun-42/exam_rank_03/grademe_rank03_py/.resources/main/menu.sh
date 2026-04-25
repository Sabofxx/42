clear
find ../rank03_py/level1 -name "tester.sh" -exec chmod +rwx {} \;
find ../rank03_py/level2 -name "tester.sh" -exec chmod +rwx {} \;

bash label.sh
bash intro.sh
