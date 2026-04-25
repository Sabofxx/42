#!/bin/bash
source colors.sh

rank=$1
level=$2

base_dir="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
subject_file="/tmp/.current_subject_${rank}_${level}"

get_subjects() {
    case "$level" in
        level1)
            echo "atoi alternate_case capitalize_words valid_palindrome valid_anagram merge_and_sort_desc sorted"
            ;;
        level2)
            echo "brackets convert_base mirror_matrix mirror_matrix_vertical rotate_90 whisper_lipher"
            ;;
        *)
            echo ""
            ;;
    esac
}

pick_new_subject() {
    subjects_list=$(get_subjects)
    IFS=' ' read -r -a qsub <<< "$subjects_list"
    count=${#qsub[@]}
    random_index=$(( RANDOM % count ))
    chosen="${qsub[$random_index]}"
    echo "$chosen" > "$subject_file"
}

prepare_subject() {
    mkdir -p "$base_dir/../../rendu/$chosen"
    touch "$base_dir/../../rendu/$chosen/$chosen.py"

    cd "$base_dir/../$rank/$level/$chosen" || {
        echo -e "${RED}Subject folder not found.${RESET}"
        exit 1
    }

    clear
    echo -e "${CYAN}${BOLD}Your subject: $chosen${RESET}"
    echo "=================================================="
    cat sub.txt
    echo
    echo "=================================================="
    echo -e "${YELLOW}Type 'test' to test your code, 'next' to get a new question, or 'exit' to quit.${RESET}"
}

# Initial subject selection
if [ -f "$subject_file" ]; then
    chosen=$(cat "$subject_file")
    echo -e "${BLUE}Resuming with previously chosen subject: $chosen${RESET}"
else
    pick_new_subject
    chosen=$(cat "$subject_file")
    echo -e "${GREEN}New subject chosen: $chosen${RESET}"
fi

prepare_subject

# Interactive loop
while true; do
    echo -e "${MAGENTA}${BOLD}Enter command: ${RESET}"
    read command

    case $command in
        test)
            if [ -f "tester.sh" ]; then
                echo -e "${BLUE}Running tester...${RESET}"
                bash tester.sh
                echo -e "${CYAN}Test completed. Continue working or type 'next' for a new subject.${RESET}"
            else
                echo -e "${YELLOW}No tester available for this subject. Please test manually.${RESET}"
            fi
            ;;
        next)
            pick_new_subject
            chosen=$(cat "$subject_file")
            echo -e "${GREEN}New subject chosen: $chosen${RESET}"
            prepare_subject
            ;;
        exit)
            echo -e "${RED}Exiting exam mode...${RESET}"
            rm -f "$subject_file"
            cd "$base_dir"
            exit 0
            ;;
        *)
            echo -e "${RED}Unknown command. Use 'test', 'next', or 'exit'.${RESET}"
            ;;
    esac
done
