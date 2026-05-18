#!/bin/bash
# ABOUTME: Semi-automated answer quality check for RAG Against the Machine.
# ABOUTME: Lists valid questions, lets corrector pick 3, runs answer generation for manual review.
#
# Usage: ./exam_answer.sh --student-path PATH --moulinette-path PATH [--questions Q1,Q2,Q3]
# Pass criteria: Corrector judges 2/3 answers as satisfactory

set -e

# --- Argument parsing ---
STUDENT_PATH=""
MOULINETTE_PATH=""
SELECTED_QUESTIONS=""
MODULE_NAME="src"

usage() {
    echo "Usage: $0 --student-path PATH --moulinette-path PATH [--questions Q1,Q2,Q3] [--module-name NAME]"
    echo ""
    echo "Required arguments:"
    echo "  --student-path PATH       Path to student code directory"
    echo "  --moulinette-path PATH    Path to moulinette binary or directory"
    echo ""
    echo "Optional arguments:"
    echo "  --questions Q1,Q2,Q3      Comma-separated question texts to test (skip interactive selection)"
    echo "  --module-name NAME        Python module name (default: src)"
    exit 1
}

while [[ $# -gt 0 ]]; do
    case "$1" in
        --student-path)
            STUDENT_PATH="$2"
            shift 2
            ;;
        --moulinette-path)
            MOULINETTE_PATH="$2"
            shift 2
            ;;
        --questions)
            SELECTED_QUESTIONS="$2"
            shift 2
            ;;
        --module-name)
            MODULE_NAME="$2"
            shift 2
            ;;
        *)
            echo "Error: Unknown argument: $1"
            usage
            ;;
    esac
done

if [ -z "$STUDENT_PATH" ] || [ -z "$MOULINETTE_PATH" ]; then
    echo "Error: Both --student-path and --moulinette-path are required."
    usage
fi

if [ ! -d "$STUDENT_PATH" ]; then
    echo "Error: Student path is not a directory: $STUDENT_PATH"
    exit 1
fi

# Resolve to absolute paths
STUDENT_PATH="$(cd "$STUDENT_PATH" && pwd)"
if [ -d "$MOULINETTE_PATH" ]; then
    MOULINETTE_PATH="$(cd "$MOULINETTE_PATH" && pwd)"
else
    MOULINETTE_PATH="$(cd "$(dirname "$MOULINETTE_PATH")" && pwd)/$(basename "$MOULINETTE_PATH")"
fi

# --- Configuration ---
SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
DATETIME=$(date +"%Y-%m-%d_%H-%M-%S")
PROJECT_DIR="$(cd "$SCRIPT_DIR/../.." && pwd)"
EVAL_DIR="$PROJECT_DIR/evaluations/answer/$DATETIME"

# Dataset paths
DOCS_DATASET="$PROJECT_DIR/data/datasets/private/AnsweredQuestions/dataset_docs_private.json"
# Search for results: first in evaluations/ (from exam_retrieval.sh), then data/output/
DOCS_SEARCH_RESULTS_DIR=""
LATEST_EVAL=$(find "$PROJECT_DIR/evaluations/retrieval" -name "search_results" -type d 2>/dev/null | sort -r | head -1)
if [ -n "$LATEST_EVAL" ]; then
    DOCS_SEARCH_RESULTS_DIR="$LATEST_EVAL"
else
    DOCS_SEARCH_RESULTS_DIR="$PROJECT_DIR/data/output/search_results"
fi

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BOLD='\033[1m'
NC='\033[0m'

# Helper: run moulinette command
run_moulinette() {
    if [ -d "$MOULINETTE_PATH" ]; then
        cd "$MOULINETTE_PATH"
        uv run python -m moulinette "$@"
    else
        "$MOULINETTE_PATH" "$@"
    fi
}

echo -e "${YELLOW}==============================================${NC}"
echo -e "${YELLOW}ANSWER QUALITY EXAMINATION${NC}"
echo -e "${YELLOW}==============================================${NC}"
echo "Student path: $STUDENT_PATH"
echo "Moulinette path: $MOULINETTE_PATH"
echo "Eval directory: $EVAL_DIR"
echo -e "${YELLOW}==============================================${NC}"

mkdir -p "$EVAL_DIR"

# --- Step 1: List valid questions ---
echo ""
echo -e "${YELLOW}--- Step 1: Listing valid questions (sources found) ---${NC}"

# Find docs search results
DOCS_RESULTS=$(find "$DOCS_SEARCH_RESULTS_DIR" -name "*docs*private*" -type f 2>/dev/null | head -1)
if [ -z "$DOCS_RESULTS" ]; then
    echo -e "${RED}Error: No docs search results found.${NC}"
    echo "Run exam_retrieval.sh first, or check data/output/search_results/"
    exit 1
fi

echo "Using search results: $DOCS_RESULTS"
echo ""

run_moulinette list_valid_questions \
    --student_answer_path "$DOCS_RESULTS" \
    --dataset_path "$DOCS_DATASET" \
    --k 10 \
    2>&1 | tee "$EVAL_DIR/valid_questions.log" || {
    echo -e "${YELLOW}WARNING: list_valid_questions failed. This may indicate a schema"
    echo -e "mismatch in the search results file. You can still select questions"
    echo -e "manually or use --questions to pre-select them.${NC}"
}

# --- Step 2: Select questions ---
echo ""
echo -e "${YELLOW}--- Step 2: Question Selection ---${NC}"

if [ -n "$SELECTED_QUESTIONS" ]; then
    echo "Using pre-selected questions: $SELECTED_QUESTIONS"
    IFS=',' read -ra QUESTIONS <<< "$SELECTED_QUESTIONS"
else
    echo -e "${BOLD}From the [VALID] questions above, pick 3 question texts to test.${NC}"
    echo "Enter each question (copy the text between quotes), then press Enter."
    echo ""
    QUESTIONS=()
    for i in 1 2 3; do
        echo -n "Question $i: "
        read -r q
        QUESTIONS+=("$q")
    done
fi

# --- Step 3: Run answers and display ---
echo ""
echo -e "${YELLOW}--- Step 3: Running answer generation ---${NC}"

ANSWER_NUM=0
for question in "${QUESTIONS[@]}"; do
    ((ANSWER_NUM++)) || true
    echo ""
    echo -e "${YELLOW}--- Answer $ANSWER_NUM/3 ---${NC}"
    echo -e "${BOLD}Question:${NC} $question"
    echo ""

    cd "$STUDENT_PATH"
    echo -e "${BOLD}Student answer:${NC}"
    uv run python -m $MODULE_NAME answer "$question" --k 10 \
        2> "$EVAL_DIR/answer_${ANSWER_NUM}_stderr.log" \
        | tee "$EVAL_DIR/answer_${ANSWER_NUM}.log"

    echo ""
    echo "---"
done

# --- Step 4: Corrector judgment ---
echo ""
echo -e "${YELLOW}==============================================${NC}"
echo -e "${YELLOW}CORRECTOR JUDGMENT${NC}"
echo -e "${YELLOW}==============================================${NC}"
echo ""
echo "Review the 3 answers above."
echo "Pass criteria: at least 2 out of 3 answers are satisfactory."
echo ""
echo "A satisfactory answer:"
echo "  - Addresses the question asked"
echo "  - Contains relevant information from the vLLM codebase"
echo "  - Is coherent and understandable"
echo ""
echo "Results saved to: $EVAL_DIR"
echo ""
echo -e "${BOLD}Does the student pass? (2/3 satisfactory answers required)${NC}"
