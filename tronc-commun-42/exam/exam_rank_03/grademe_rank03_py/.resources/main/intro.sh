source colors.sh
mkdir -p ../../rendu
clear
bash label.sh
printf "${CYAN}%s${RESET}\n" "╔═══════════════════════════════════════════════════════════╗"
printf "${BLUE}%s${GREEN}%s${BLUE}%s${RESET}\n" "║" "   ⚡ EXAM 42 RANK 03 PYTHON - PRACTICE ⚡   " "║"
printf "${BLUE}%s${YELLOW}%s${BLUE}%s${RESET}\n" "║" "          Made by omischle @ 42           " "║"
printf "${CYAN}%s${RESET}\n" "╠═══════════════════════════════════════════════════════════╣"
printf "${BLUE}%s${RESET}\n" "▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓"
printf "${GREEN}%s${RESET}\n"  "◆◇◆◇◆◇◆◇◆◇◆◇◆◇◆◇◆◇◆◇◆◇◆◇◆◇◆◇◆◇◆◇◆◇◆◇◆◇◆◇◆◇◆◇◆◇◆◇◆◇◆◇◆◇◆◇◆"
printf "${YELLOW}${BOLD}%s${RESET}\n" "🔥 1. Level Mode (choose level)"
printf "${YELLOW}${BOLD}%s${RESET}\n" "🧪 2. Real Exam Mode (random)"
printf "${YELLOW}${BOLD}%s${RESET}\n" "📁 3. Open Rendu Folder"
printf "${GREEN}%s${RESET}\n"  "◆◇◆◇◆◇◆◇◆◇◆◇◆◇◆◇◆◇◆◇◆◇◆◇◆◇◆◇◆◇◆◇◆◇◆◇◆◇◆◇◆◇◆◇◆◇◆◇◆◇◆◇◆◇◆◇◆"
printf "${BLUE}%s${RESET}\n" "▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓"
printf "${CYAN}%s${RESET}\n" "╚═══════════════════════════════════════════════════════════╝"
printf "${GREEN}${BOLD}Enter your choice (1-3): ${RESET}"
read opt
case $opt in
    1)
        bash rank03_py.sh
        ;;
    2)
        bash rank03_py_real_mode.sh
        ;;
    3)
        cd ../../rendu
        open .
        cd ../.resources/main
        bash intro.sh
        ;;
    exit)
        cd ../../
        rm -rf rendu
        clear
        exit 0
        ;;
    *)
        echo "Invalid choice. Please enter 1, 2, or 3."
        sleep 1
        bash intro.sh
        ;;
esac
