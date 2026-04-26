*This project has been created as part of the 42 curriculum by omischle.*

# Codexion

## Description

**Codexion** is a multithreaded simulation written in C. A pool of
*coders* compete for a shared set of *dongles* under a configurable
real-time scheduling policy (FIFO or EDF — Earliest Deadline First).
Each coder cycles through the same task — acquire a dongle, compile,
debug and refactor — within a strict burnout deadline. If a coder
cannot complete its work before the deadline, the simulation halts and
the offending coder is reported. Optionally, the simulation also stops
once every coder has reached a target number of completed compiles.

The project exercises the same skills as the classic *Philosophers*
project (mutexes, condition variables, priority queues, time-critical
logging) and adds a pluggable scheduler on top.

## Instructions

### Prerequisites

- A C compiler that accepts `-Wall -Wextra -Werror -pthread`
  (`cc` / `gcc` / `clang`)
- POSIX threads (`pthread`)

### Build

The actual project sources live under `coders/`. From this directory:

```bash
cd coders
make            # builds the ./codexion binary
```

Other Makefile targets:

| Command | Description |
|---|---|
| `make` / `make all` | Build the `codexion` binary |
| `make clean` | Remove object files |
| `make fclean` | Remove object files and the binary |
| `make re` | `fclean` + `all` |

### Run

```bash
./codexion <n_coders> <t_burnout> <t_compile> <t_debug> <t_refactor> \
           <compiles_req> <cooldown> <scheduler>
```

| Argument | Meaning |
|---|---|
| `n_coders` | Number of coders (≥ 1) |
| `t_burnout` | Burnout deadline in ms — a coder that does not complete a compile within this window after its previous one is reported |
| `t_compile` | Time required to compile (ms) |
| `t_debug` | Time required to debug (ms) |
| `t_refactor` | Time required to refactor (ms) |
| `compiles_req` | If > 0, the simulation stops once every coder has reached this many compiles |
| `cooldown` | Minimum time (ms) before a released dongle can be re-acquired |
| `scheduler` | Scheduling policy for waiters on a busy dongle: `fifo` or `edf` |

Example:
```bash
./codexion 5 800 200 200 100 0 50 edf
```

## Technical choices

- **One thread per coder** + a single monitor thread. The monitor wakes
  on a fast timer to detect burnouts and to check whether the
  `compiles_req` exit condition has been met.
- **One mutex + one condition variable per dongle**, with a
  per-dongle priority queue of waiting coders. A coder that cannot
  acquire a dongle immediately enqueues a request and waits on the
  condition variable.
- **Pluggable scheduler** via a function pointer (`cmp_request`) on the
  priority queue. `fifo` orders by request time; `edf` orders by
  remaining time before burnout.
- **Cooldown** prevents a single coder from monopolising a dongle:
  after a release, the dongle records `released_at` and rejects any
  acquire attempt before `released_at + cooldown`.
- **Logging through one shared mutex** (`log_mtx`) so that messages
  emitted by different threads never interleave.
- **No memory leaks, no data races** — every `malloc` is paired with a
  matching `free` in `destroy_sim`, and every shared structure is
  protected by a documented mutex.

## Resources

- *The Linux Programming Interface*, Michael Kerrisk — chapters on
  POSIX threads, mutexes and condition variables.
- [`pthread_create(3)`](https://man7.org/linux/man-pages/man3/pthread_create.3.html),
  [`pthread_mutex_lock(3)`](https://man7.org/linux/man-pages/man3/pthread_mutex_lock.3.html),
  [`pthread_cond_wait(3)`](https://man7.org/linux/man-pages/man3/pthread_cond_wait.3.html)
- *Real-Time Systems*, Jane W. S. Liu — for the EDF scheduling policy.
- 42 *Philosophers* project — closest cousin in the curriculum.
- [`gettimeofday(2)`](https://man7.org/linux/man-pages/man2/gettimeofday.2.html)
  for monotonic millisecond timestamps.

### AI usage in this project

| Task | Tool | Where |
|---|---|---|
| Sketching the priority-queue layout | Claude / ChatGPT | Design phase |
| Reviewing the dongle acquire/release contract for races | Claude | `srcs/dongle.c`, `srcs/dongle_acquire.c` — read line by line by hand |
| Drafting README sections | Claude | This file — reviewed manually |

All AI-generated content was reviewed, understood and validated before
inclusion. No code was kept without full comprehension.
