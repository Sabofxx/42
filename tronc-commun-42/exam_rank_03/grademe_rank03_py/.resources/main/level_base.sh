#!/bin/bash
source colors.sh

rank=$1
level=$2

base_dir="$(cd "$(dirname "$0")" && pwd)"

# Set question array based on level
if [[ "$level" == *"level1"* ]]; then
    qsub=(atoi alternate_case capitalize_words valid_palindrome valid_anagram merge_and_sort_desc sorted)
elif [[ "$level" == *"level2"* ]]; then
    qsub=(brackets convert_base mirror_matrix mirror_matrix_vertical rotate_90 whisper_lipher)
else
    echo "Invalid level: $level"
    exit 1
fi

# Shuffle questions
shuffle_array() {
    local i tmp size max rand
    size=${#qsub[*]}
    max=$(( 32768 / size * size ))

    for ((i = size - 1; i > 0; i--)); do
        while (( (rand = RANDOM) >= max )); do :; done
        rand=$(( rand % (i + 1) ))
        tmp=${qsub[i]}
        qsub[i]=${qsub[rand]}
        qsub[rand]=$tmp
    done
    shuffled=("${qsub[@]}")
}

shuffle_array
num=${#shuffled[@]}
i=0
cd "../$rank/$level/${shuffled[$i]}"

while true; do
    cd "../${shuffled[$i]}"
    mkdir -p "$base_dir/../../rendu/${shuffled[$i]}"
    touch "$base_dir/../../rendu/${shuffled[$i]}/${shuffled[$i]}.py"

    subject=$(cat sub.txt)

    # Check if all questions are completed
    if [ $i -ge $num ]; then
        clear
        echo "These questions at $level are completed."
        echo "=============================================="
        read -rp "${GREEN}${BOLD}Please press enter for return to the menu.${RESET}" enterx
        sleep 2
        cd ../../main
        bash menu.sh
        exit
    fi

    # Inner loop for testing or navigating
    while true; do
        clear
        echo -e "${WHITE}$subject${RESET}"
        echo
        echo "Please type 'test' to test code, 'next' for next or 'exit' for exit."
        echo
        read -rp "/>" input
        case $input in
            next)
                i=$((i+1))
                break
                ;;
            test)
                clear
                ./tester.sh &
                pid=$!
                slept=0

                while [ $slept -lt 10 ] && kill -0 $pid 2>/dev/null; do
                    sleep 1
                    slept=$((slept+1))
                done

                if kill -0 $pid 2>/dev/null; then
                    echo "$(tput setaf 1)$(tput bold)TIMEOUT$(tput sgr 0)"
                    echo "It can be because of infinite loop"
                    echo "Please check your code or just try again."
                    kill $pid 2>/dev/null
                fi

                echo "=============================================="
                read -rp "${GREEN}${BOLD}Please press enter to continue your practice.${RESET}" enter
                break
                ;;
            menu)
                cd ../../../../
                if [ -d rendu ]; then
                    mkdir -p trace
                    cp -r rendu "trace/rendu_backup_$(date +%s)"
                    rm -rf rendu
                fi
                cd .resources/main
                bash menu.sh
                exit
                ;;
            exit)
                cd ../../../../
                if [ -d rendu ]; then
                    mkdir -p trace
                    cp -r rendu "trace/rendu_backup_$(date +%s)"
                    rm -rf rendu
                fi
                exit 0
                ;;
            *)
                echo "Please type 'test' to test code, 'next' for next or 'exit' to quit."
                ;;
        esac
    done
done
