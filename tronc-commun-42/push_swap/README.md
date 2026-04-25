*This project has been created as part of the 42 curriculum by omischle.*

## Description
`push_swap` is a sorting project using two stacks (`a` and `b`) and a strict instruction set (`sa`, `sb`, `ss`, `pa`, `pb`, `ra`, `rb`, `rr`, `rra`, `rrb`, `rrr`).

The goal is to output a valid operation sequence that sorts stack `a` in ascending order with as few operations as possible.

This repository implements the mandatory requirements from the subject:
- parsing and error handling (`Error\n` on stderr)
- four embedded strategies
- runtime strategy selection via flags
- adaptive mode based on the disorder metric
- optional `--bench` metrics on stderr

## Author
- `omischle`

## Instructions
### Build
```bash
make
```

Mandatory targets available:
- `all`
- `clean`
- `fclean`
- `re`

### Run
Default behavior uses adaptive selection:
```bash
./push_swap 2 1 3 6 5 8
```

You can force a strategy:
```bash
./push_swap --simple  5 4 3 2 1
./push_swap --medium  5 4 3 2 1
./push_swap --complex 5 4 3 2 1
./push_swap --adaptive 5 4 3 2 1
```

Enable benchmark output (printed on `stderr`):
```bash
./push_swap --bench --adaptive 4 67 3 87 23
```

Count operations:
```bash
ARG="4 67 3 87 23"
./push_swap $ARG | wc -l
```

Check with provided checker binary:
```bash
ARG="4 67 3 87 23"
./push_swap --complex $ARG | ./checker_Mac\ \(1\) $ARG
```

## Parsing and Error Rules
- Accepted input: signed integers in 32-bit range
- Duplicates are forbidden
- Invalid tokens or out-of-range values produce `Error` on stderr
- With no numeric input, program prints nothing and exits

## Algorithms and Strategy Design
The project embeds four strategies and selects one at runtime.

### 1) Simple strategy (`--simple`) — `O(n^2)`
Technique: repeated minimum extraction.
- Rotate/reverse-rotate `a` to bring min to top
- `pb` to `b`
- Repeat until small base case
- Push back to `a`

This is a straightforward quadratic baseline in push_swap operation model.

### 2) Medium strategy (`--medium`) — `O(n * sqrt(n))`
Technique: chunk-based partitioning with chunk size close to `sqrt(n)`.
- Push ranges from `a` to `b`
- Use rotations to keep `b` structured
- Rebuild `a` by retrieving maxima from `b`

Chunk count scales with `sqrt(n)`, giving medium complexity behavior.

### 3) Complex strategy (`--complex`) — `O(n log n)`
Technique: radix sort adaptation on normalized indices.
- Normalize values to ranks (`index`)
- Bitwise passes (LSD)
- `pb`/`ra` partition per bit, then merge back with `pa`

This provides logarithmic number of passes over `n` elements.

### 4) Adaptive strategy (`--adaptive`, default)
Adaptive chooses internal method using mandatory disorder metric computed before moves:
- low disorder: `< 0.2` -> simple (`O(n^2)`)
- medium disorder: `0.2 <= disorder < 0.5` -> medium (`O(n * sqrt(n))`)
- high disorder: `>= 0.5` -> complex (`O(n log n)`)

Rationale:
- nearly sorted inputs can be handled efficiently with simple local moves
- moderately disordered inputs benefit from chunk partitioning
- highly disordered inputs are best handled by radix-based global partitioning

## Complexity Notes (Push_swap Model)
Complexity statements in this project refer to the number of generated push_swap operations, not classic array assignment/comparison counts.

Space usage remains linear due to stack nodes and temporary arrays used for index normalization/parsing.

## Benchmark Output (`--bench`)
When `--bench` is enabled, the program prints to `stderr`:
- disorder percentage (2 decimals)
- chosen strategy and complexity class
- total number of operations
- per-operation counters for all 11 operations

The operation sequence itself remains on `stdout`.

## Performance
Observed random tests are within mandatory thresholds:
- `100` numbers: below `2000` operations (project measured around `1084`)
- `500` numbers: below `12000` operations (project measured around `7396`)

## Resources
### Classic References
- 42 subject: Push_swap (v1.1)
- Donald Knuth, algorithm analysis references (Big-O fundamentals)
- Standard C library and Unix man pages (`read`, `write`, `malloc`, `free`, `exit`)

### AI Usage Disclosure
AI assistance was used for:
- drafting implementation structure
- discussing algorithm tradeoffs and complexity interpretations in push_swap operation model
- helping prepare and format project documentation

All generated ideas/code were manually reviewed, tested, and adapted to fit the subject, Norm, and project constraints.
