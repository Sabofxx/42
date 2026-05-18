#!/bin/bash
# ABOUTME: Edge case and reliability testing for RAG Against the Machine.
# ABOUTME: Tests that the system handles degenerate inputs without Python tracebacks.
#
# Usage: ./exam_edge_cases.sh --student-path PATH
# Pass criteria: All 4 tests complete without Python tracebacks

set -e

# --- Argument parsing ---
STUDENT_PATH=""
MODULE_NAME="src"

usage() {
    echo "Usage: $0 --student-path PATH [--module-name NAME]"
    echo ""
    echo "Required arguments:"
    echo "  --student-path PATH       Path to student code directory"
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

if [ -z "$STUDENT_PATH" ]; then
    echo "Error: --student-path is required."
    usage
fi

if [ ! -d "$STUDENT_PATH" ]; then
    echo "Error: Student path is not a directory: $STUDENT_PATH"
    exit 1
fi

# Resolve to absolute path
STUDENT_PATH="$(cd "$STUDENT_PATH" && pwd)"

# --- Configuration ---
SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
DATETIME=$(date +"%Y-%m-%d_%H-%M-%S")
PROJECT_DIR="$(cd "$SCRIPT_DIR/../.." && pwd)"
EVAL_DIR="$PROJECT_DIR/evaluations/edge_cases/$DATETIME"

# Counters
TESTS_PASSED=0
TESTS_TOTAL=4

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m'

echo -e "${YELLOW}==============================================${NC}"
echo -e "${YELLOW}EDGE CASE EXAMINATION${NC}"
echo -e "${YELLOW}==============================================${NC}"
echo "Student path: $STUDENT_PATH"
echo "Eval directory: $EVAL_DIR"
echo -e "${YELLOW}==============================================${NC}"

mkdir -p "$EVAL_DIR"

cd "$STUDENT_PATH"

# Helper: run a command and check for Python tracebacks in stderr
run_edge_test() {
    local test_num="$1"
    local test_name="$2"
    local cmd="$3"

    echo ""
    echo -e "${YELLOW}--- Test $test_num/$TESTS_TOTAL: $test_name ---${NC}"
    echo "  Command: $cmd"

    # Run command, allow it to fail (exit code != 0 is OK for edge cases)
    eval "$cmd" > "$EVAL_DIR/test_${test_num}_stdout.log" 2> "$EVAL_DIR/test_${test_num}_stderr.log" || true

    # Check for Python tracebacks in stderr
    if grep -q "Traceback (most recent call last)" "$EVAL_DIR/test_${test_num}_stderr.log"; then
        echo -e "  ${RED}FAILED: Python traceback detected${NC}"
        echo "  Traceback excerpt:"
        tail -5 "$EVAL_DIR/test_${test_num}_stderr.log" | sed 's/^/    /'
        echo "TEST_$test_num ($test_name): FAIL (traceback)" >> "$EVAL_DIR/summary.log"
    else
        echo -e "  ${GREEN}PASSED: No traceback${NC}"
        echo "TEST_$test_num ($test_name): PASS" >> "$EVAL_DIR/summary.log"
        ((TESTS_PASSED++)) || true
    fi
}

# --- Test 1: Empty query ---
run_edge_test 1 "Empty query" \
    "uv run python -m $MODULE_NAME search '' --k 10"

# --- Test 2: Gibberish query ---
run_edge_test 2 "Gibberish query" \
    "uv run python -m $MODULE_NAME search 'asdfghjkl zxcvbnm qwertyuiop' --k 10"

# --- Test 3: k=0 ---
run_edge_test 3 "k=0 answer" \
    "uv run python -m $MODULE_NAME answer 'What is vLLM?' --k 0"

# --- Test 4: Bad dataset path ---
run_edge_test 4 "Nonexistent dataset path" \
    "uv run python -m $MODULE_NAME search_dataset --dataset_path /nonexistent/dataset.json --k 10"

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
