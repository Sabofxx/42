#!/bin/bash

# Exam simulator for 42 Python common-core
# Manages 6 levels: 2 Easy, 2 Medium, 2 Hard
# For easy levels: randomly selects from 6 available exercises

# Directory setup
SUBJECTS_DIR="./subjects"
RENDU_DIR="./rendu"
TRACES_DIR="./traces"
STATE_FILE="./.exam_state"
HISTORY_FILE="./.exam_history"

EASY_EXERCISES=(
    "py_mirror_matrix|/rendu/py_mirror_matrix/|Write a function that mirrors a 2D matrix horizontally by reversing each row.|def mirror_matrix(matrix: list[list[int]]) -> list[list[int]]:|Input: mirror_matrix([[1, 2, 3], [4, 5, 6]]) → Output: [[3, 2, 1], [6, 5, 4]]\nInput: mirror_matrix([[1, 2], [3, 4], [5, 6]]) → Output: [[2, 1], [4, 3], [6, 5]]\nInput: mirror_matrix([[7]]) → Output: [[7]]\nInput: mirror_matrix([[1, 2, 3, 4]]) → Output: [[4, 3, 2, 1]]|python3 -c \"from ejercicio import mirror_matrix; assert mirror_matrix([[1,2,3],[4,5,6]]) == [[3,2,1],[6,5,4]]; assert mirror_matrix([[1,2],[3,4],[5,6]]) == [[2,1],[4,3],[6,5]]; assert mirror_matrix([[7]]) == [[7]]; assert mirror_matrix([[1,2,3,4]]) == [[4,3,2,1]]\"|mirror_matrix"
    "py_echo_validator|/rendu/py_echo_validator/|Write a function that checks if a string is a palindrome, ignoring spaces and case, only consider alphabetic characters.|def echo_validator(text: str) -> bool:|Input: echo_validator('racecar') → Output: True\nInput: echo_validator('A man a plan a canal Panama') → Output: True\nInput: echo_validator('race a car') → Output: False\nInput: echo_validator('Was it a car or a cat I saw') → Output: True\nInput: echo_validator('hello') → Output: False\nInput: echo_validator('Madam Im Adam') → Output: True\nInput: echo_validator('') → Output: False|python3 -c \"from ejercicio import echo_validator; assert echo_validator('racecar') == True; assert echo_validator('A man a plan a canal Panama') == True; assert echo_validator('race a car') == False; assert echo_validator('Was it a car or a cat I saw') == True; assert echo_validator('hello') == False; assert echo_validator('Madam Im Adam') == True; assert echo_validator('') == False\"|echo_validator"
    "py_whisper_cipher|/rendu/py_whisper_cipher/|Write a function that creates a simple cipher by shifting letters in a string by a given amount. Non-alphabetic characters should remain unchanged.|def whisper_cipher(text: str, shift: int) -> str:|Input: whisper_cipher('hello', 3) → Output: 'khoor'\nInput: whisper_cipher('Hello World!', 1) → Output: 'Ifmmp Xpsme!'\nInput: whisper_cipher('xyz', 3) → Output: 'abc'\nInput: whisper_cipher('ABC123def', 5) → Output: 'FGH123ijk'\nInput: whisper_cipher('', 10) → Output: ''|python3 -c \"from ejercicio import whisper_cipher; assert whisper_cipher('hello', 3) == 'khoor'; assert whisper_cipher('Hello World!', 1) == 'Ifmmp Xpsme!'; assert whisper_cipher('xyz', 3) == 'abc'; assert whisper_cipher('ABC123def', 5) == 'FGH123ijk'; assert whisper_cipher('', 10) == ''\"|whisper_cipher"
    "py_shadow_merge|/rendu/py_shadow_merge/|Write a function that merges two sorted lists into one sorted list.|def shadow_merge(list1: list[int], list2: list[int]) -> list[int]:|Input: shadow_merge([1, 3, 5], [2, 4, 6]) → Output: [1, 2, 3, 4, 5, 6]\nInput: shadow_merge([1, 2, 3], [4, 5, 6]) → Output: [1, 2, 3, 4, 5, 6]\nInput: shadow_merge([1], [2, 3, 4]) → Output: [1, 2, 3, 4]\nInput: shadow_merge([], [1, 2, 3]) → Output: [1, 2, 3]\nInput: shadow_merge([1, 1, 2], [1, 3, 3]) → Output: [1, 1, 1, 2, 3, 3]|python3 -c \"from ejercicio import shadow_merge; assert shadow_merge([1,3,5], [2,4,6]) == [1,2,3,4,5,6]; assert shadow_merge([1,2,3], [4,5,6]) == [1,2,3,4,5,6]; assert shadow_merge([1], [2,3,4]) == [1,2,3,4]; assert shadow_merge([], [1,2,3]) == [1,2,3]; assert shadow_merge([1,1,2], [1,3,3]) == [1,1,1,2,3,3]\"|shadow_merge"
)

MEDIUM_EXERCISES=(
    "py_number_base_converter|/rendu/py_number_base_converter/|Write a function that converts a number from one base to another. Support bases from 2 to 36 inclusive. Return 'ERROR' for invalid inputs.|def number_base_converter(number: str, from_base: int, to_base: int) -> str:|Input: number_base_converter('1010', 2, 10) → Output: '10'\nInput: number_base_converter('FF', 16, 10) → Output: '255'\nInput: number_base_converter('255', 10, 16) → Output: 'FF'\nInput: number_base_converter('123', 10, 2) → Output: '1111011'\nInput: number_base_converter('Z', 36, 10) → Output: '35'\nInput: number_base_converter('35', 10, 36) → Output: 'Z'\nInput: number_base_converter('123', 1, 10) → Output: 'ERROR'\nInput: number_base_converter('G', 16, 10) → Output: 'ERROR'|python3 -c \"from ejercicio import number_base_converter; assert number_base_converter('1010', 2, 10) == '10'; assert number_base_converter('FF', 16, 10) == '255'; assert number_base_converter('255', 10, 16) == 'FF'; assert number_base_converter('123', 10, 2) == '1111011'; assert number_base_converter('Z', 36, 10) == '35'; assert number_base_converter('35', 10, 36) == 'Z'; assert number_base_converter('123', 1, 10) == 'ERROR'; assert number_base_converter('G', 16, 10) == 'ERROR'\"|number_base_converter"
    "py_bracket_validator|/rendu/py_bracket_validator/|Write a function that checks if brackets [], parentheses (), and braces {} are properly balanced and correctly nested. All other characters are ignored.|def bracket_validator(s: str) -> bool:|Input: bracket_validator('()') → Output: True\nInput: bracket_validator('()[]{}') → Output: True\nInput: bracket_validator('(]') → Output: False\nInput: bracket_validator('([)]') → Output: False\nInput: bracket_validator('{[]}') → Output: True\nInput: bracket_validator('hello(world)[test]{code}') → Output: True\nInput: bracket_validator('((()))') → Output: True\nInput: bracket_validator('((())') → Output: False\nInput: bracket_validator('') → Output: True|python3 -c \"from ejercicio import bracket_validator; assert bracket_validator('()') == True; assert bracket_validator('()[]{}') == True; assert bracket_validator('(]') == False; assert bracket_validator('([)]') == False; assert bracket_validator('{[]}') == True; assert bracket_validator('hello(world)[test]{code}') == True; assert bracket_validator('((()))') == True; assert bracket_validator('((())') == False; assert bracket_validator('') == True\"|bracket_validator"
    "py_pattern_tracker|/rendu/py_pattern_tracker/|Write a function that counts the number of valid consecutive digit pairs in a string. A valid pair consists of two adjacent digits where the second digit is exactly one greater than the first digit.|def pattern_tracker(text: str) -> int:|Input: pattern_tracker('123') → Output: 2\nInput: pattern_tracker('12a34') → Output: 2\nInput: pattern_tracker('987654321') → Output: 0\nInput: pattern_tracker('01234567') → Output: 7\nInput: pattern_tracker('abc') → Output: 0\nInput: pattern_tracker('1a2b3c4') → Output: 0\nInput: pattern_tracker('112233') → Output: 2|python3 -c \"from ejercicio import pattern_tracker; assert pattern_tracker('123') == 2; assert pattern_tracker('12a34') == 2; assert pattern_tracker('987654321') == 0; assert pattern_tracker('01234567') == 7; assert pattern_tracker('abc') == 0; assert pattern_tracker('1a2b3c4') == 0; assert pattern_tracker('112233') == 2\"|pattern_tracker"
    "py_string_sculptor|/rendu/py_string_sculptor/|Write a function that transforms a string by alternating the case of alphabetic characters only. The first alphabetic character should be lowercase, the second uppercase, etc.|def string_sculptor(text: str) -> str:|Input: string_sculptor('hello') → Output: 'hElLo'\nInput: string_sculptor('Hello World') → Output: 'hElLo wOrLd'\nInput: string_sculptor('aBc123def') → Output: 'aBc123DeF'\nInput: string_sculptor('Python3.9!') → Output: 'pYtHoN3.9!'\nInput: string_sculptor('') → Output: ''|python3 -c \"from ejercicio import string_sculptor; assert string_sculptor('hello') == 'hElLo'; assert string_sculptor('Hello World') == 'hElLo wOrLd'; assert string_sculptor('aBc123def') == 'aBc123DeF'; assert string_sculptor('Python3.9!') == 'pYtHoN3.9!'; assert string_sculptor('') == ''\"|string_sculptor"
    "py_twist_sequence|/rendu/py_twist_sequence/|Write a function that rotates an array to the right by k positions, rotating right means the last k elements move to the front.|def twist_sequence(arr: list[int], k: int) -> list[int]:|Input: twist_sequence([1, 2, 3, 4, 5], 2) → Output: [4, 5, 1, 2, 3]\nInput: twist_sequence([1, 2, 3], 1) → Output: [3, 1, 2]\nInput: twist_sequence([1, 2, 3, 4], 0) → Output: [1, 2, 3, 4]\nInput: twist_sequence([1, 2, 3], 5) → Output: [2, 3, 1]\nInput: twist_sequence([], 3) → Output: []|python3 -c \"from ejercicio import twist_sequence; assert twist_sequence([1,2,3,4,5], 2) == [4,5,1,2,3]; assert twist_sequence([1,2,3], 1) == [3,1,2]; assert twist_sequence([1,2,3,4], 0) == [1,2,3,4]; assert twist_sequence([1,2,3], 5) == [2,3,1]; assert twist_sequence([], 3) == []\"|twist_sequence"
)

HARD_EXERCISES=(
    "py_string_permutation_checker|/rendu/py_string_permutation_checker/|Write a function that determines if two strings are permutations of each other. They contain the same characters with the same frequencies.|def string_permutation_checker(s1: str, s2: str) -> bool:|Input: string_permutation_checker('abc', 'bca') → Output: True\nInput: string_permutation_checker('abc', 'def') → Output: False\nInput: string_permutation_checker('listen', 'silent') → Output: True\nInput: string_permutation_checker('hello', 'bello') → Output: False\nInput: string_permutation_checker('', '') → Output: True\nInput: string_permutation_checker('a', '') → Output: False\nInput: string_permutation_checker('Abc', 'abc') → Output: False\nInput: string_permutation_checker('a gentleman', 'elegant man') → Output: True|python3 -c \"from ejercicio import string_permutation_checker; assert string_permutation_checker('abc', 'bca') == True; assert string_permutation_checker('abc', 'def') == False; assert string_permutation_checker('listen', 'silent') == True; assert string_permutation_checker('hello', 'bello') == False; assert string_permutation_checker('', '') == True; assert string_permutation_checker('a', '') == False; assert string_permutation_checker('Abc', 'abc') == False; assert string_permutation_checker('a gentleman', 'elegant man') == True\"|string_permutation_checker"
    "py_cryptic_sorter|/rendu/py_cryptic_sorter/|Write a function that sorts a list of strings: 1) By length (shortest first), 2) ASCII order case-insensitive, 3) By number of vowels (ascending).|def cryptic_sorter(strings: list[str]) -> list[str]:|Input: cryptic_sorter(['apple', 'cat', 'banana', 'dog', 'elephant']) → Output: ['cat', 'dog', 'apple', 'banana', 'elephant']\nInput: cryptic_sorter(['aaa', 'bbb', 'AAA', 'BBB']) → Output: ['AAA', 'aaa', 'BBB', 'bbb']\nInput: cryptic_sorter(['hello', 'world', 'hi', 'test']) → Output: ['hi', 'test', 'hello', 'world']\nInput: cryptic_sorter([]) → Output: []\nInput: cryptic_sorter(['']) → Output: ['']|python3 -c \"from ejercicio import cryptic_sorter; assert cryptic_sorter(['apple', 'cat', 'banana', 'dog', 'elephant']) == ['cat', 'dog', 'apple', 'banana', 'elephant']; assert cryptic_sorter(['aaa', 'bbb', 'AAA', 'BBB']) == ['AAA', 'aaa', 'BBB', 'bbb']; assert cryptic_sorter(['hello', 'world', 'hi', 'test']) == ['hi', 'test', 'hello', 'world']; assert cryptic_sorter([]) == []; assert cryptic_sorter(['']) == ['']\"|cryptic_sorter"
)

# Initialize directories
mkdir -p "$SUBJECTS_DIR" "$RENDU_DIR" "$TRACES_DIR"

# State file format: LEVEL_INDEX:SELECTED_EXERCISE_INDEX
# Levels: 0=Easy1, 1=Easy2, 2=Medium1, 3=Medium2, 4=Hard1, 5=Hard2

# History file: comma-separated list of used exercise indices for current difficulty

load_exercise_history() {
    if [ -f "$HISTORY_FILE" ]; then
        cat "$HISTORY_FILE"
    else
        echo ""
    fi
}

save_exercise_history() {
    local new_index=$1
    local current_history=$(load_exercise_history)
    if [ -z "$current_history" ]; then
        echo "$new_index" > "$HISTORY_FILE"
    else
        echo "${current_history},${new_index}" > "$HISTORY_FILE"
    fi
}

reset_exercise_history() {
    rm -f "$HISTORY_FILE"
}

select_random_exercise() {
    local array_size=$1
    local history=$(load_exercise_history)
    local available=""
    
    if [ -z "$history" ]; then
        shuf -n 1 -i 0-$((array_size - 1))
    else
        for i in $(seq 0 $((array_size - 1))); do
            if ! echo ",$history," | grep -q ",$i,"; then
                available="$available $i"
            fi
        done
        local count=$(echo "$available" | wc -w)
        if [ "$count" -eq 0 ]; then
            reset_exercise_history
            shuf -n 1 -i 0-$((array_size - 1))
        else
            echo "$available" | tr ' ' '\n' | shuf | head -1
        fi
    fi
}

# Function to display exam explanation
show_explanation() {
    echo "=== 42 Python Exam Simulator ==="
    echo ""
    echo "How it works:"
    echo "1. Run './exam.sh' or 'make' to start/exam menu"
    echo "2. The current subject will be placed in ./subjects/"
    echo "3. Work on the exercise in ./rendu/[exercise_name]/"
    echo "4. When ready, run './exam.sh grade' or 'make grade' to submit"
    echo "5. On success: subject is replaced with next level's subject"
    echo "6. On failure: error traces saved in ./traces/ showing diff"
    echo ""
    echo "Levels: 2 Easy -> 2 Medium -> 2 Hard (in order)"
    echo "Note: For Easy levels, a random exercise is selected from the pool"
    echo ""
}

get_current_level() {
    if [ -f "$STATE_FILE" ]; then
        cat "$STATE_FILE" | cut -d':' -f1
    else
        echo "0"
    fi
}

get_selected_exercise_index() {
    if [ -f "$STATE_FILE" ]; then
        cat "$STATE_FILE" | cut -d':' -f2
    else
        echo "-1"
    fi
}

set_state() {
    local level=$1
    local exercise_index=$2
    echo "${level}:${exercise_index}" > "$STATE_FILE"
}

reset_exam() {
    echo "0:-1" > "$STATE_FILE"
    reset_exercise_history
    rm -rf "$SUBJECTS_DIR"/* "$TRACES_DIR"/* 2>/dev/null || true
    echo "Exam reset. Starting from level 1 (Easy)."
}

clean_exam() {
    rm -rf "$SUBJECTS_DIR"/* "$TRACES_DIR"/* 2>/dev/null || true
    rm -f "$STATE_FILE" "$HISTORY_FILE"
    echo "All generated files cleaned."
    
    read -p "Do you also want to delete all exercises in rendu/? (y/n) " -n 1 -r
    echo
    
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        rm -rf "$RENDU_DIR"/* 2>/dev/null || true
        echo "Exercises deleted from rendu/"
    else
        echo "Keeping exercises in rendu/"
    fi
}

get_level_info() {
    local level=$1
    case $level in
        0) echo "Easy 1" ;;
        1) echo "Easy 2" ;;
        2) echo "Medium 1" ;;
        3) echo "Medium 2" ;;
        4) echo "Hard 1" ;;
        5) echo "Hard 2" ;;
        *) echo "Unknown" ;;
    esac
}

load_exercise() {
    local level=$1
    local level_name=$(get_level_info $level)
    
    echo "Loading exercise for $level_name (Level $((level+1))/6)..."
    
    rm -f "$SUBJECTS_DIR"/* 2>/dev/null || true
    
    local exercise_data=""
    local selected_index=-1
    
    if [ $level -lt 2 ]; then
        local easy_count=${#EASY_EXERCISES[@]}
        selected_index=$(select_random_exercise $easy_count)
        exercise_data="${EASY_EXERCISES[$selected_index]}"
        save_exercise_history "$selected_index"
    elif [ $level -lt 4 ]; then
        selected_index=$((level - 2))
        exercise_data="${MEDIUM_EXERCISES[$selected_index]}"
    else
        selected_index=$((level - 4))
        exercise_data="${HARD_EXERCISES[$selected_index]}"
    fi
    
    if [ -z "$exercise_data" ]; then
        echo "Error: No exercise data found for level $level"
        return 1
    fi
    
    IFS='|' read -r exercise_name folder subject_content signature examples test_command function_name <<< "$exercise_data"
    
    if [ -z "$folder" ] || [ -z "$exercise_name" ]; then
        echo "Error: Invalid exercise data at index $selected_index"
        return 1
    fi
    
    folder_name=$(basename "$folder" 2>/dev/null)
    if [ -z "$folder_name" ]; then
        folder_name=$(echo "$exercise_name" | tr '[:upper:]' '[:lower:]')
    fi
    
    local func_name_from_exercise=$(echo "$function_name" | tr '[:upper:]' '[:lower:]')
    local new_sig="def py_${function_name}${signature#"def ${func_name_from_exercise}"}"
    new_sig="${new_sig%:}:"
    
    {
        echo "Assignment | $folder"
        echo "Files to submit | $folder_name.py"
        echo ""
        echo "$subject_content"
        echo ""
        echo "Function signature:"
        echo "$new_sig"
        echo ""
        echo "Examples:"
        echo "======================================="
        echo -e "$examples"
    } > "$SUBJECTS_DIR/subject_en.txt"
    
    folder_name=$(echo "$exercise_name" | tr '[:upper:]' '[:lower:]')
    test_command=$(echo "$test_command" | sed "s/from ejercicio import/from $folder_name import/")
    
    set_state $level $selected_index
}

grade_exercise() {
    local current_level=$(get_current_level)
    local level_name=$(get_level_info $current_level)
    local selected_exercise_index=$(get_selected_exercise_index)
    local subject_file="$SUBJECTS_DIR/subject_en.txt"
    
    local test_command=""
    local function_name=""
    local exercise_name=""
    local folder_name=""
    
    local selected_index=-1
    
    if [ $current_level -lt 2 ]; then
        if [ $current_level -eq 0 ]; then
            selected_index=$(get_selected_exercise_index)
            if [ $selected_index -lt 0 ] || [ $selected_index -ge ${#EASY_EXERCISES[@]} ]; then
                selected_index=$(select_random_exercise ${#EASY_EXERCISES[@]})
            fi
        else
            selected_index=$(get_selected_exercise_index)
            if [ $selected_index -lt 0 ] || [ $selected_index -ge ${#EASY_EXERCISES[@]} ]; then
                selected_index=$(select_random_exercise ${#EASY_EXERCISES[@]})
            fi
        fi
        IFS='|' read -r exercise_name _ _ _ _ test_command function_name <<< "${EASY_EXERCISES[$selected_index]}"
    elif [ $current_level -lt 4 ]; then
        local index=$((current_level - 2))
        IFS='|' read -r exercise_name _ _ _ _ test_command function_name <<< "${MEDIUM_EXERCISES[$index]}"
    else
        local index=$((current_level - 4))
        IFS='|' read -r exercise_name _ _ _ _ test_command function_name <<< "${HARD_EXERCISES[$index]}"
    fi
    
    folder_name=$(echo "$exercise_name" | tr '[:upper:]' '[:lower:]')
    
    local python_path="${folder_name}/${folder_name}.py"
    local import_wrapper="import importlib.util; spec = importlib.util.spec_from_file_location('${folder_name}', '${python_path}'); mod = importlib.util.module_from_spec(spec); spec.loader.exec_module(mod); "
    
    local asserts=$(echo "$test_command" | sed 's/.*-c "\(.*\)"/\1/')
    asserts=$(echo "$asserts" | sed "s/from [^ ]* import ${function_name}; //")
    asserts=$(echo "$asserts" | sed "s/\b${function_name}(/mod.py_${function_name}(/g")
    test_command="python3 -c \"${import_wrapper}${asserts}\""
    
    function_name="$folder_name"
    
    local exercise_dir="$RENDU_DIR/$folder_name"
    local exercise_file="$exercise_dir/$folder_name.py"
    
    echo "Grading $level_name exercise..."
    
    if [ ! -d "$exercise_dir" ] || [ ! -f "$exercise_file" ]; then
        echo "Error: No $folder_name.py found in $exercise_dir."
        echo "Please create the directory and the file manually."
        return 1
    fi
    
    echo "Running tests for function: $function_name"
    
    local original_dir=$(pwd)
    local test_result=0
    local test_output=""
    
    cd "$RENDU_DIR" && eval "$test_command" > /tmp/test_output_$$.txt 2>&1
    test_result=$?
    test_output=$(cat /tmp/test_output_$$.txt)
    rm -f /tmp/test_output_$$.txt
    
    if [ $test_result -eq 0 ]; then
        echo "$test_output" | head -20
    fi
    
    cd "$original_dir" 2>/dev/null
    
    if [ $test_result -eq 0 ]; then
        echo "✓ Exercise passed! Moving to next level..."
        
        rm -f "$subject_file"
        
        local next_level=$((current_level + 1))
        if [ $next_level -lt 6 ]; then
            if [ $next_level -ge 2 ]; then
                reset_exercise_history
            fi
            set_state $next_level -1
            load_exercise $next_level
        else
            echo "Congratulations! You have completed all 6 levels."
            set_state 0 -1
            reset_exercise_history
        fi
        
        return 0
    else
        echo "✗ Exercise failed. Your code did not pass the tests."
        
        local trace_file="$TRACES_DIR/trace_level_$((current_level+1))_$(date +%s).txt"
        {
            echo "=== Trace for $level_name (Failed Attempt) ==="
            echo "Timestamp: $(date)"
            echo "Level: $level_name"
            echo "Exercise: $folder_name"
            echo "Function to implement: $function_name"
            echo ""
            echo "Test command that failed:"
            echo "$test_command"
            echo ""
            echo "Please check your implementation of the '$function_name' function and try again."
            echo ""
            echo "Current content of your file:"
            cat "$exercise_file"
        } > "$trace_file"
        
        echo "Traces saved to: $trace_file"
        echo "Please check your implementation and try again."
        
        return 1
    fi
}

case "$1" in
    grade)
        grade_exercise
        ;;
    reset|re)
        reset_exam
        ;;
    clean)
        clean_exam
        ;;
    *)
        show_explanation
        
        if [ ! -f "$STATE_FILE" ]; then
            echo "Initializing exam..."
            set_state 0 -1
            load_exercise 0
        else
            current_level=$(get_current_level)
            level_name=$(get_level_info $current_level)
            selected_index=$(get_selected_exercise_index)
            echo "Current level: $level_name (Level $((current_level+1))/6)"
            if [ $current_level -lt 2 ] && [ $selected_index -ge 0 ]; then
                echo "Selected exercise: $(echo "${EASY_EXERCISES[$selected_index]}" | cut -d'|' -f1)"
            fi
            if [ ! -f "$SUBJECTS_DIR/subject_en.txt" ]; then
                echo "Loading exercise..."
                load_exercise $current_level
            fi
            echo "Subject located in: $SUBJECTS_DIR/"
            echo "User creates: mkdir $RENDU_DIR/<exercise_folder> && touch $RENDU_DIR/<exercise_folder>/<exercise_folder>.py"
            echo ""
            echo "Commands:"
            echo "  make grade  - Submit current exercise for grading"
            echo "  make re    - Reset exam to beginning"
            echo "  make clean - Clean all generated files"
        fi
        ;;
esac