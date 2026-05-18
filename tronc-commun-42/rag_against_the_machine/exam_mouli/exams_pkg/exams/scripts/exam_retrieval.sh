#!/bin/bash
# ABOUTME: Automated retrieval evaluation script for RAG Against the Machine.
# ABOUTME: Tests indexing time, retrieval throughput, and Recall@5 against private datasets.
#
# Usage: ./exam_retrieval.sh --student-path PATH --moulinette-path PATH
# Pass criteria: indexing <=300s, warm retrieval <=90s for 200 questions,
#                docs Recall@5 >= 80%, code Recall@5 >= 50%

set -e

# --- Argument parsing ---
STUDENT_PATH="/home/omischle/goinfre/f/intra-uuid-294d728e-bd9b-4b97-91b2-c49d79f55144-7408939-omischle/src/student/"
MOULINETTE_PATH="/home/omischle/goinfre/f/intra-uuid-294d728e-bd9b-4b97-91b2-c49d79f55144-7408939-omischle/exam_mouli/moulinette_pkg/"
MODULE_NAME="src"

usage() {
    echo "Usage: $0 --student-path PATH --moulinette-path PATH [--module-name NAME]"
    echo ""
    echo "Required arguments:"
    echo "  --student-path PATH       Path to student code directory"
    echo "  --moulinette-path PATH    Path to moulinette binary or directory"
    echo ""
    echo "Optional arguments:"
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

# Validate required arguments
if [ -z "$STUDENT_PATH" ] || [ -z "$MOULINETTE_PATH" ]; then
    echo "Error: Both arguments are required."
    usage
fi

if [ ! -d "$STUDENT_PATH" ]; then
    echo "Error: Student path is not a directory: $STUDENT_PATH"
    exit 1
fi

# Moulinette path can be a directory (run via uv) or a binary file
if [ ! -d "$MOULINETTE_PATH" ] && [ ! -f "$MOULINETTE_PATH" ]; then
    echo "Error: Moulinette path not found: $MOULINETTE_PATH"
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
PROJECT_DIR="$(cd "$SCRIPT_DIR/../../" && pwd)"
EVAL_DIR="$PROJECT_DIR/evaluations/retrieval/$DATETIME"

# Private dataset paths (relative to student project root)
DOCS_DATASET="$PROJECT_DIR/data/datasets/private/AnsweredQuestions/dataset_docs_private.json"
CODE_DATASET="$PROJECT_DIR/data/datasets/private/AnsweredQuestions/dataset_code_private.json"
DOCS_UNANSWERED="$PROJECT_DIR/data/datasets/private/UnansweredQuestions/dataset_docs_private.json"
CODE_UNANSWERED="$PROJECT_DIR/data/datasets/private/UnansweredQuestions/dataset_code_private.json"
SEARCH_OUTPUT_DIR="$EVAL_DIR/search_results"

# Thresholds
INDEXING_TIME_LIMIT=300
WARM_RETRIEVAL_TIME_LIMIT=90
DOCS_RECALL_THRESHOLD=0.80
CODE_RECALL_THRESHOLD=0.50

# Counters
TESTS_PASSED=0
TESTS_TOTAL=4

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
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
echo -e "${YELLOW}RETRIEVAL EXAMINATION${NC}"
echo -e "${YELLOW}==============================================${NC}"
echo "Student path: $STUDENT_PATH"
echo "Moulinette path: $MOULINETTE_PATH"
echo "Eval directory: $EVAL_DIR"
echo "Docs dataset: $DOCS_DATASET"
echo "Code dataset: $CODE_DATASET"
echo -e "${YELLOW}==============================================${NC}"

mkdir -p "$EVAL_DIR"
mkdir -p "$SEARCH_OUTPUT_DIR"

# --- Check private datasets exist ---
if [ ! -f "$DOCS_DATASET" ] || [ ! -f "$CODE_DATASET" ]; then
    echo -e "${RED}Error: Private datasets not found. Unzip them first:${NC}"
    echo "  unzip data/datasets/datasets_private.zip -d data/datasets/"
    exit 1
fi

# --- Test 1: Indexing ---
echo ""
echo -e "${YELLOW}--- Test 1/4: Indexing (limit: ${INDEXING_TIME_LIMIT}s) ---${NC}"

cd "$STUDENT_PATH"
INDEX_START=$(date +%s)
uv run python -m $MODULE_NAME index --max_chunk_size 2000 \
    > "$EVAL_DIR/indexing_stdout.log" 2> "$EVAL_DIR/indexing_stderr.log" \
    && INDEX_SUCCESS=1 || INDEX_SUCCESS=0
INDEX_END=$(date +%s)
INDEX_DURATION=$((INDEX_END - INDEX_START))

if [ $INDEX_SUCCESS -eq 0 ]; then
    echo -e "${RED}FAILED: Indexing crashed (see indexing_stderr.log)${NC}"
    echo "INDEX: CRASHED (${INDEX_DURATION}s)" >> "$EVAL_DIR/summary.log"
elif [ "$INDEX_DURATION" -gt "$INDEXING_TIME_LIMIT" ]; then
    echo -e "${RED}FAILED: Indexing took ${INDEX_DURATION}s > ${INDEXING_TIME_LIMIT}s${NC}"
    echo "INDEX: EXCEEDED (${INDEX_DURATION}s > ${INDEXING_TIME_LIMIT}s)" >> "$EVAL_DIR/summary.log"
else
    echo -e "${GREEN}PASSED: Indexing completed in ${INDEX_DURATION}s (<= ${INDEXING_TIME_LIMIT}s)${NC}"
    echo "INDEX: OK (${INDEX_DURATION}s <= ${INDEXING_TIME_LIMIT}s)" >> "$EVAL_DIR/summary.log"
    ((TESTS_PASSED++)) || true
fi

# --- Test 2: Warm Retrieval Throughput ---
echo ""
echo -e "${YELLOW}--- Test 2/4: Warm Retrieval Throughput (200 questions in <= ${WARM_RETRIEVAL_TIME_LIMIT}s) ---${NC}"

cd "$STUDENT_PATH"

# Run search_dataset on docs
echo "  Running search_dataset on docs..."
DOCS_SEARCH_START=$(date +%s)
uv run python -m $MODULE_NAME search_dataset \
    --dataset_path "$DOCS_UNANSWERED" \
    --k 10 \
    --save_directory "$SEARCH_OUTPUT_DIR" \
    > "$EVAL_DIR/search_docs_stdout.log" 2> "$EVAL_DIR/search_docs_stderr.log" \
    && DOCS_SEARCH_SUCCESS=1 || DOCS_SEARCH_SUCCESS=0
DOCS_SEARCH_END=$(date +%s)
DOCS_SEARCH_DURATION=$((DOCS_SEARCH_END - DOCS_SEARCH_START))
echo "  Docs search: ${DOCS_SEARCH_DURATION}s"

# Run search_dataset on code
echo "  Running search_dataset on code..."
CODE_SEARCH_START=$(date +%s)
uv run python -m $MODULE_NAME search_dataset \
    --dataset_path "$CODE_UNANSWERED" \
    --k 10 \
    --save_directory "$SEARCH_OUTPUT_DIR" \
    > "$EVAL_DIR/search_code_stdout.log" 2> "$EVAL_DIR/search_code_stderr.log" \
    && CODE_SEARCH_SUCCESS=1 || CODE_SEARCH_SUCCESS=0
CODE_SEARCH_END=$(date +%s)
CODE_SEARCH_DURATION=$((CODE_SEARCH_END - CODE_SEARCH_START))
echo "  Code search: ${CODE_SEARCH_DURATION}s"

TOTAL_SEARCH_DURATION=$((DOCS_SEARCH_DURATION + CODE_SEARCH_DURATION))

if [ $DOCS_SEARCH_SUCCESS -eq 0 ] || [ $CODE_SEARCH_SUCCESS -eq 0 ]; then
    echo -e "${RED}FAILED: search_dataset crashed (check logs)${NC}"
    echo "THROUGHPUT: CRASHED" >> "$EVAL_DIR/summary.log"
elif [ "$TOTAL_SEARCH_DURATION" -gt "$WARM_RETRIEVAL_TIME_LIMIT" ]; then
    echo -e "${RED}FAILED: Warm retrieval took ${TOTAL_SEARCH_DURATION}s > ${WARM_RETRIEVAL_TIME_LIMIT}s${NC}"
    echo "THROUGHPUT: EXCEEDED (${TOTAL_SEARCH_DURATION}s > ${WARM_RETRIEVAL_TIME_LIMIT}s)" >> "$EVAL_DIR/summary.log"
else
    echo -e "${GREEN}PASSED: 200 questions retrieved in ${TOTAL_SEARCH_DURATION}s (<= ${WARM_RETRIEVAL_TIME_LIMIT}s)${NC}"
    echo "THROUGHPUT: OK (${TOTAL_SEARCH_DURATION}s <= ${WARM_RETRIEVAL_TIME_LIMIT}s)" >> "$EVAL_DIR/summary.log"
    ((TESTS_PASSED++)) || true
fi

# --- Test 3: Docs Recall@5 ---
echo ""
echo -e "${YELLOW}--- Test 3/4: Docs Recall@5 (threshold: ${DOCS_RECALL_THRESHOLD}) ---${NC}"

# Find the docs search results file
DOCS_RESULTS=$(find "$SEARCH_OUTPUT_DIR" -name "*docs*" -type f 2>/dev/null | head -1)
if [ -z "$DOCS_RESULTS" ]; then
    echo -e "${RED}FAILED: No docs search results found in $SEARCH_OUTPUT_DIR${NC}"
    echo "DOCS_RECALL: NO RESULTS FILE" >> "$EVAL_DIR/summary.log"
else
    echo "  Evaluating: $DOCS_RESULTS"
    DOCS_EVAL_OUTPUT=$(run_moulinette evaluate_student_search_results \
        "$DOCS_RESULTS" "$DOCS_DATASET" \
        --k 10 --max_context_length 2000 --threshold "$DOCS_RECALL_THRESHOLD" 2>&1) \
        && DOCS_EVAL_SUCCESS=1 || DOCS_EVAL_SUCCESS=0
    echo "$DOCS_EVAL_OUTPUT" | tee "$EVAL_DIR/docs_eval.log"

    if echo "$DOCS_EVAL_OUTPUT" | grep -q "^PASS:"; then
        echo -e "${GREEN}PASSED: Docs Recall@5 meets threshold${NC}"
        echo "DOCS_RECALL: PASS" >> "$EVAL_DIR/summary.log"
        ((TESTS_PASSED++)) || true
    else
        echo -e "${RED}FAILED: Docs Recall@5 below threshold${NC}"
        echo "DOCS_RECALL: FAIL" >> "$EVAL_DIR/summary.log"
    fi
fi

# --- Test 4: Code Recall@5 ---
echo ""
echo -e "${YELLOW}--- Test 4/4: Code Recall@5 (threshold: ${CODE_RECALL_THRESHOLD}) ---${NC}"

CODE_RESULTS=$(find "$SEARCH_OUTPUT_DIR" -name "*code*" -type f 2>/dev/null | head -1)
if [ -z "$CODE_RESULTS" ]; then
    echo -e "${RED}FAILED: No code search results found in $SEARCH_OUTPUT_DIR${NC}"
    echo "CODE_RECALL: NO RESULTS FILE" >> "$EVAL_DIR/summary.log"
else
    echo "  Evaluating: $CODE_RESULTS"
    CODE_EVAL_OUTPUT=$(run_moulinette evaluate_student_search_results \
        "$CODE_RESULTS" "$CODE_DATASET" \
        --k 10 --max_context_length 2000 --threshold "$CODE_RECALL_THRESHOLD" 2>&1) \
        && CODE_EVAL_SUCCESS=1 || CODE_EVAL_SUCCESS=0
    echo "$CODE_EVAL_OUTPUT" | tee "$EVAL_DIR/code_eval.log"

    if echo "$CODE_EVAL_OUTPUT" | grep -q "^PASS:"; then
        echo -e "${GREEN}PASSED: Code Recall@5 meets threshold${NC}"
        echo "CODE_RECALL: PASS" >> "$EVAL_DIR/summary.log"
        ((TESTS_PASSED++)) || true
    else
        echo -e "${RED}FAILED: Code Recall@5 below threshold${NC}"
        echo "CODE_RECALL: FAIL" >> "$EVAL_DIR/summary.log"
    fi
fi

# --- Extract exact recall values for star ratings ---
echo ""
echo -e "${YELLOW}--- Recall Values for Star Ratings ---${NC}"

# Parse recall@5 from eval logs
DOCS_RECALL_VALUE=""
CODE_RECALL_VALUE=""
if [ -f "$EVAL_DIR/docs_eval.log" ]; then
    DOCS_RECALL_VALUE=$(grep 'Recall@5 = ' "$EVAL_DIR/docs_eval.log" | head -1 | sed 's/.*Recall@5 = \([0-9.]*\).*/\1/')
    echo "  Docs Recall@5 = ${DOCS_RECALL_VALUE:-N/A}"
fi
if [ -f "$EVAL_DIR/code_eval.log" ]; then
    CODE_RECALL_VALUE=$(grep 'Recall@5 = ' "$EVAL_DIR/code_eval.log" | head -1 | sed 's/.*Recall@5 = \([0-9.]*\).*/\1/')
    echo "  Code Recall@5 = ${CODE_RECALL_VALUE:-N/A}"
fi

echo ""
echo "  Star rating reference (Docs, base 80%):"
echo "    2 stars: >= 80%  |  3 stars: >= 85%  |  4 stars: >= 90%  |  5 stars: >= 95%"
echo "  Star rating reference (Code, base 50%):"
echo "    2 stars: >= 50%  |  3 stars: >= 55%  |  4 stars: >= 60%  |  5 stars: >= 65%"

# --- Final Summary ---
echo ""
echo -e "${YELLOW}==============================================${NC}"
echo -e "${YELLOW}FINAL RESULT: $TESTS_PASSED/$TESTS_TOTAL${NC}"
echo -e "${YELLOW}==============================================${NC}"
echo "Results saved to: $EVAL_DIR"

if [ $TESTS_PASSED -eq $TESTS_TOTAL ]; then
    echo -e "${GREEN}STATUS: PASS${NC}"
    exit 0
else
    echo -e "${RED}STATUS: FAIL ($TESTS_PASSED/$TESTS_TOTAL passed)${NC}"
    exit 1
fi
