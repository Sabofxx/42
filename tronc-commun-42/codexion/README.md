*This project has been created as part of the 42 curriculum by omischle.*

# Codexion

## Description

**Codexion** is a concurrent simulation of `N` coders competing for a shared
pool of `N` USB dongles arranged in a ring. Every coder needs **two adjacent
dongles** to compile, and each compile must be followed by a debug phase and
a refactor phase. If a coder waits too long between two compiles, they
**burn out** and the simulation ends in failure.

The project is a generalisation of the classical *Dining Philosophers* problem
with three additional twists:

- A **per-dongle cooldown**: a dongle that has just been released cannot be
  acquired again for `cooldown` ms. This forces the scheduler to actually
  schedule, instead of letting one greedy coder monopolise a resource.
- An explicit **scheduling policy** chosen on the command line:
  - `fifo` — first-come, first-served (timestamp of arrival as priority key)
  - `edf` — Earliest-Deadline-First (next burnout instant as priority key)
- A **monitor thread** that detects burnouts and end-of-simulation conditions
  in real time, with millisecond precision.

The goal is to write a deadlock-free, starvation-free, leak-free C program
that satisfies all the above with `pthread` primitives only.

## Instructions

### Prerequisites

- A POSIX system with `pthread` support (Linux or macOS)
- `cc` / `clang` / `gcc` with `-pthread`
- `make`

### Build

```bash
cd coders
make           # builds ./codexion
make re        # full rebuild
make clean     # remove .o files
make fclean    # remove .o files and the binary
```

The build is `-Wall -Wextra -Werror -pthread` clean.

### Run

The program takes **8 positional arguments**:

```
./codexion <n> <t_burnout> <t_compile> <t_debug> <t_refactor> <compiles_req> <cooldown> <fifo|edf>
```

| Argument | Meaning | Unit |
|---|---|---|
| `n` | number of coders / dongles | integer ≥ 1 |
| `t_burnout` | max time between two compile *starts* | ms |
| `t_compile` | duration of a compile | ms |
| `t_debug` | duration of a debug | ms |
| `t_refactor` | duration of a refactor | ms |
| `compiles_req` | compiles required per coder before success | integer ≥ 0 |
| `cooldown` | per-dongle cooldown after release | ms |
| `fifo` / `edf` | scheduling policy | string |

### Examples

```bash
# Comfortable parameters — every coder finishes
./codexion 5 1500 200 200 200 5 50 fifo

# Tight parameters — at least one coder will burn out
./codexion 5 600 200 200 200 5 50 fifo

# EDF policy — late coders are served first
./codexion 5 1500 200 200 200 5 50 edf

# Edge case n=1 — a lone coder cannot compile (needs 2 distinct dongles)
./codexion 1 800 200 200 200 5 50 fifo
```

### Output format

Each event is printed on its own line as:

```
<elapsed_ms> <coder_id> <message>
```

Possible messages: `has taken a dongle`, `is compiling`, `is debugging`,
`is refactoring`, `burned out`. The `burned out` message ends the
simulation and is guaranteed to be the **last** line of output.

## Blocking cases handled

This section describes every concurrency hazard the implementation
explicitly defends against.

### Deadlock prevention — Coffman conditions

A deadlock can occur if and only if all four **Coffman conditions**
(Coffman, Elphick, Shoshani, 1971) hold simultaneously:

1. **Mutual exclusion** — a dongle is held by at most one coder.
2. **Hold and wait** — a coder holds its first dongle while waiting for the second.
3. **No preemption** — a held dongle cannot be forcibly taken; the holder must release it.
4. **Circular wait** — a cycle of coders, each waiting on the next one's dongle.

Conditions 1, 2 and 3 are inherent to the problem: a dongle is a mutex,
the coder needs both dongles to compile, and we never preempt. The
implementation therefore breaks the **circular wait** condition by
imposing a **total order on resource acquisition**:

```c
/* dongle.c */
left  = c->id - 1;
right = c->id % c->sim->n;
first  = min(left, right);   /* always acquire lowest id first  */
second = max(left, right);   /* then the higher id              */
```

With this rule, no cycle in the wait-for graph can exist: if a coder
is blocked on a dongle, it can only be blocked on one with a strictly
greater id than the one it already holds. There is no "back-edge", so
there is no cycle, so there is no deadlock.

### Starvation prevention

With FIFO, the priority key is the timestamp of the request. Any waiter
already in the queue has a strictly smaller key than any future arrival,
so it will eventually become the head of the heap and be served when
the dongle is free and its cooldown has expired.

With EDF, the priority key is `last_compile + t_burnout`, which is the
moment the coder will burn out. The waiter closest to its deadline is
always served first, which both prevents starvation and minimises the
risk of a real burnout in tight schedules.

In both modes, a request is removed from the queue *only* when the coder
either acquires the dongle (`pq_pop`) or aborts because the simulation
was stopped (`pq_remove`). A pending request is never silently dropped.

### Cooldown handling

After a dongle is released it stores `released_at = now_ms()` and
broadcasts on its condition variable. The acquisition predicate is:

```c
static int can_take(t_dongle *d, int coder_id)
{
    return !d->in_use
        && pq_peek(&d->waiters)->coder_id == coder_id
        && now_ms() >= d->released_at + d->cooldown;
}
```

Even if a waiter is at the head of the queue and the dongle is free,
the cooldown can hold acquisition back. The waiting loop uses
`pthread_cond_timedwait` with a 10 ms timeout so the predicate is
re-checked every 10 ms, allowing the coder to acquire the dongle
immediately after the cooldown elapses without spinning.

### Precise burnout detection

The monitor thread polls every 500 µs. For each coder it computes:

```c
since = now_ms() - get_last_compile(coder);
if (since >= sim->t_burnout)
    /* coder has burned out */
```

`last_compile` is updated at the **start** of every compile (after the
two dongles are held), under the coder's per-coder mutex. The same
mutex is used by the monitor when reading `last_compile`, so there is
no race on the value. This places the burnout check resolution at
roughly 0.5 ms — well below any realistic value of `t_burnout`.

### Log serialization (no print after stop)

`log_state`, `log_burnout` and `sim_stopped` all share the same global
mutex `log_mtx`. The invariant is:

> Once a thread sets `sim->stop = 1` while holding `log_mtx`, no other
> thread can print again, because every print path locks `log_mtx`
> first and then checks `if (!sim->stop) printf(...)`.

This makes the `... burned out` line **always** the last line of
output, with no interleaved or trailing event. It is also why
`sim_stopped()` reads `stop` under `log_mtx` rather than directly: the
read needs to see the same value the writer last published.

### Clean shutdown

`precise_sleep` checks `sim_stopped` every 200 µs, so a thread that is
in the middle of a compile/debug/refactor exits within microseconds of
`stop` being set instead of finishing the full sleep. Threads waiting
in `acquire_dongle` either time out on `pthread_cond_timedwait` (10 ms)
or are woken by a `pthread_cond_broadcast` issued on every release, so
no thread can stay blocked after shutdown is requested.

## Thread synchronization mechanisms

This section explains how each `pthread` primitive is used and how
they coordinate.

### `pthread_mutex_t`

| Mutex | Where | Protects |
|---|---|---|
| `t_dongle::lock` | one per dongle | `in_use`, `released_at`, the `waiters` priority queue |
| `t_coder::mtx` | one per coder | `last_compile`, `compiles_done` |
| `t_sim::log_mtx` | one global | `stop` flag and any write to stdout |

Every shared variable is owned by exactly one mutex. A thread that
needs to read or write a variable always locks the corresponding mutex
first. This serialises all access and removes data races at compile
time — the variables are never declared `volatile` or `_Atomic`,
because the locks already provide both atomicity and the memory
fence/release semantics required for inter-thread visibility.

### `pthread_cond_t`

Each dongle has one condition variable `t_dongle::cond` paired with
its mutex. The waiting protocol is the textbook pattern:

```c
pthread_mutex_lock(&d->lock);
pq_push(&d->waiters, request);
while (!can_take(d, coder_id))
{
    if (sim_stopped(sim)) { pq_remove(...); break; }
    pthread_cond_timedwait(&d->cond, &d->lock, 10ms_from_now);
}
pq_pop(&d->waiters);
d->in_use = 1;
pthread_mutex_unlock(&d->lock);
```

`release_dongle` sets `released_at`, clears `in_use` and calls
`pthread_cond_broadcast`. Broadcast (not signal) is correct here
because only the head of the heap is allowed to acquire, but when the
head is blocked by the cooldown we still want every thread to wake up
and re-check — otherwise a state change could be missed.

The 10 ms timeout on `cond_timedwait` is what makes the cooldown work
without a dedicated timer: even if no thread broadcasts, every waiter
re-checks the predicate at 10 ms granularity, so a request that
becomes valid because `now_ms()` crossed the cooldown threshold is
served within 10 ms.

### Custom priority queue (no extra primitives)

A binary min-heap `t_pq` of `t_request{coder_id, key}` is embedded in
each dongle. It is **not** a thread-safe data structure on its own —
its safety comes from the fact that every operation on it is performed
while holding the parent dongle's mutex. The comparator is supplied at
init (`cmp_request`), which is what lets the same heap implement both
FIFO (key = arrival timestamp) and EDF (key = `last_compile + t_burnout`).

### Thread-safe communication: coders ↔ monitor

There is no message passing in this project. All communication is via
shared state, and every shared state has a mutex.

**Coder publishes its progress, monitor reads it:**

```c
/* writer (coder.c) */
void update_last_compile(t_coder *c)
{
    pthread_mutex_lock(&c->mtx);
    c->last_compile = now_ms();
    pthread_mutex_unlock(&c->mtx);
}

/* reader (monitor.c) */
long get_last_compile(t_coder *c)
{
    long v;
    pthread_mutex_lock(&c->mtx);
    v = c->last_compile;
    pthread_mutex_unlock(&c->mtx);
    return v;
}
```

`compiles_done` follows the exact same pattern with a getter and a
setter that lock `c->mtx`. The monitor reads `last_compile` and
`compiles_done` for every coder once per polling iteration; under
`c->mtx` it sees a consistent snapshot.

**Monitor publishes the stop signal, coders read it:**

```c
/* writer (monitor.c) */
pthread_mutex_lock(&sim->log_mtx);
if (!sim->stop) {
    printf("%ld %d burned out\n", now_ms() - sim->start_ms, id);
    sim->stop = 1;
}
pthread_mutex_unlock(&sim->log_mtx);

/* reader (utils.c) */
int sim_stopped(t_sim *sim)
{
    int v;
    pthread_mutex_lock(&sim->log_mtx);
    v = sim->stop;
    pthread_mutex_unlock(&sim->log_mtx);
    return v;
}
```

Putting the print of `... burned out` and the `stop = 1` assignment
inside the same critical section is what makes `... burned out`
provably the **last** line printed: no other thread can hold
`log_mtx` while the burnout message is being printed, and once the
message is printed every other thread now sees `stop = 1` next time
it locks `log_mtx`.

### Race condition prevention — concrete examples

- **Race on `last_compile`** — prevented because every read and every
  write of `last_compile` goes through `get_last_compile` /
  `update_last_compile`, both of which lock `c->mtx`. There is no
  unguarded direct access.
- **Race on the dongle queue** — `pq_push`, `pq_pop`, `pq_peek` and
  `pq_remove` are *only* called between `pthread_mutex_lock(&d->lock)`
  and `pthread_mutex_unlock(&d->lock)`. The queue is not exposed.
- **Lost wake-up** — prevented because waiters call `cond_timedwait`
  *while holding* `d->lock` and *only after* checking `can_take`
  under that same lock; a release that toggles `in_use` and broadcasts
  cannot interleave between the check and the wait.
- **Print after stop** — prevented because `log_state` and
  `log_burnout` both hold `log_mtx` while checking `!stop` and while
  setting `stop = 1`, so the toggle is atomic with respect to all
  prints.

### Resource lifecycle

`init_sim` initialises mutexes and condition variables one by one. If
any single init fails, that structure is fully torn down before
returning, and the global cleanup function `destroy_sim` only walks
structures whose `inited` flag is set to 1. After `pthread_join` returns
for all coder threads and the monitor thread, `destroy_sim` is the only
function still touching the mutexes — guaranteeing that no
`pthread_mutex_destroy` ever runs on a mutex still held or waited on
by a live thread. The program runs `0 leaks for 0 total leaked bytes`
under macOS `leaks --atExit`.

## Resources

- **The Little Book of Semaphores**, Allen B. Downey — Chapter on
  Dining Philosophers, the canonical reference for resource
  acquisition order.
- **System Deadlocks**, E. G. Coffman, M. J. Elphick, A. Shoshani,
  *ACM Computing Surveys*, 1971 — the original paper formalising the
  four conditions.
- **Operating System Concepts**, Silberschatz, Galvin, Gagne — the
  chapters on synchronization, deadlock and condition variables.
- **POSIX Threads Programming**, Blaise Barney, LLNL — practical
  reference for `pthread_mutex_*`, `pthread_cond_*`, `pthread_join`.
- **Earliest-Deadline-First Scheduling**, C. L. Liu and J. W. Layland,
  *Journal of the ACM*, 1973 — the classical reference for EDF.
- **Linux man pages**: `pthread_create(3)`, `pthread_mutex_lock(3p)`,
  `pthread_cond_timedwait(3p)`, `gettimeofday(2)`, `usleep(3)`.

### AI usage in this project

| Task | Tool | Where |
|---|---|---|
| Brainstorming on how to structure the EDF/FIFO scheduler around a single priority queue | Claude | Design phase, before any code was written |
| Sanity-checking the Coffman-condition argument against the actual acquisition order | Claude | Reviewed and rephrased manually |
| Drafting parts of this README | Claude | This file — every section was reviewed, edited and validated by hand against the actual source code |

All AI-assisted content was reviewed, understood, and validated
before inclusion. No code was copied without full comprehension of
its behaviour and synchronization implications.
