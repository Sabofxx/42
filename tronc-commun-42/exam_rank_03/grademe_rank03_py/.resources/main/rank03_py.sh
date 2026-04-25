#!/bin/bash
source functions.sh
source colors.sh
clear
bash label.sh
printf "${BLUE}%s${RESET}\n" "┌─────────────────────────────────────────────────────────┐"
printf "${BLUE}%s${GREEN}%s${BLUE}%s${RESET}\n" "│" "  🎯 Choose your practice level for Exam 42 Rank 03  🎯  " "│"
printf "${BLUE}%s${RESET}\n" "└─────────────────────────────────────────────────────────┘"
printf "${CYAN}%s${RESET}\n" "∼∼∼∼∼∼∼∼∼∼∼∼∼∼∼∼∼∼∼∼∼∼∼∼∼∼∼∼∼∼∼∼∼∼∼∼∼∼∼∼∼∼∼∼∼∼∼∼∼∼∼∼∼∼∼∼∼"
printf "${YELLOW}${BOLD}%s${RESET}\n" "🔥 1. Level1 - Basics (atoi, strings, lists)"
printf "${YELLOW}${BOLD}%s${RESET}\n" "💎 2. Level2 - Advanced (matrices, cipher, brackets)"
printf "${CYAN}%s${RESET}\n" "∼∼∼∼∼∼∼∼∼∼∼∼∼∼∼∼∼∼∼∼∼∼∼∼∼∼∼∼∼∼∼∼∼∼∼∼∼∼∼∼∼∼∼∼∼∼∼∼∼∼∼∼∼∼∼∼∼"
printf "${GREEN}${BOLD}Enter your choice (1-2): ${RESET}"
read opt

case $opt in
    menu)
        bash menu.sh
        ;;
    1)
        clear
        echo "$(tput setaf 2)$(tput bold)Level 1 is being prepared...$(tput sgr0)"
        display_animation
        clear
        bash level_base.sh rank03_py level1
        ;;
    2)
        clear
        echo "$(tput setaf 2)$(tput bold)Level 2 is being prepared...$(tput sgr0)"
        display_animation
        clear
        bash level_base.sh rank03_py level2
        ;;
    exit)
        cd ../../
        rm -rf rendu
        clear
        exit 0
        ;;
    *)
        echo "$(tput setaf 1)Wrong input$(tput sgr0)"
        sleep 1
        bash rank03_py.sh
        ;;
esac
