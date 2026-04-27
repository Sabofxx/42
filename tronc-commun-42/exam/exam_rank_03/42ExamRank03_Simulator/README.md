# 42 Python Exam Simulator

A bash-based exam simulator for 42 school's Python common-core. Manages 6 levels (4 Easy, 5 Medium, 2 Hard) with automated testing.

## Quick Start

```bash
make         # Start exam / show menu
make grade   # Submit current exercise for grading
make re      # Reset exam to beginning
make clean   # Clean all generated files
```

## How It Works

1. Run `make` to get the current exercise subject
2. Read the subject in `subjects/subject_en.txt`
3. Create your exercise directory and implement the required function in `<exercise_file>.py`:
   ```bash
   mkdir rendu/<exercise_folder>
   touch rendu/<exercise_folder>/<exercise_file>.py
   ```
4. Run `make grade` to test your solution
5. Pass → advance to next level; Fail → trace saved to `traces/`
6. If you have completed the exam and/or wish to start another one, do the following:
    - ```make clean```: deletes trace files, subjects and Python temporary files (you will be asked if you also wish to delete the code for the exercises you have completed).
    - ```make re```: resets the exam to level 1.
    - ```make```: Restarts the exam.

## Traces explanation
The trace files contain:
- trace details (exercise/level where the error occurred, timestamp, exercise requirements, etc.)
- the command executed in the failed test
- the contents of your submitted file (if available)

To find out what error the program is returning, you will need to go to ```rendu/``` and run the command shown in the trace there.
The command will display an AssertionError and highlight one or more tests in red; these are the inputs that have failed.

From there, you can run tests with that input to identify the error and correct it.

## Directory Structure

```
.
├── exam.sh              # Main script
├── Makefile           # Build commands
├── subjects/          # Exercise subjects (subject_en.txt)
├── rendu/            # Student work (<exercise_folder>/ejercicio.py)
├── traces/           # Failed attempt traces
└── .exam_state       # Progress (level:exercise_index)
```

## Exercises

### Easy (4 exercises)
- **py_mirror_matrix** - Mirror a 2D matrix horizontally
- **py_echo_validator** - Palindrome checker (ignore spaces/case)
- **py_whisper_cipher** - Caesar cipher (shift letters)
- **py_shadow_merge** - Merge two sorted lists

### Medium (5 exercises)
- **py_number_base_converter** - Convert between bases 2-36
- **py_bracket_validator** - Validate balanced brackets `[](){}`
- **py_pattern_tracker** - Count consecutive digit pairs
- **py_string_sculptor** - Alternate case of letters
- **py_twist_sequence** - Rotate array right by k

### Hard (2 exercises)
- **py_string_permutation_checker** - Check if strings are permutations
- **py_cryptic_sorter** - Sort by length, case-insensitive, vowel count

## Customizing Exercises

Edit `EASY_EXERCISES`, `MEDIUM_EXERCISES`, and `HARD_EXERCISES` arrays in `exam.sh`:

```bash
# Format: NAME|SUBJECT|TEST_COMMAND|FUNCTION_NAME
EASY_EXERCISES=(
    "my_exercise|Write a function...|python3 -c \"from ejercicio import my_func; assert my_func(...) == ...\"|my_func"
)
```

## Requirements

- Bash (Linux/macOS/WSL)
- Python 3