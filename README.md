# JUGGLER — Water Jug AI Laboratory

A terminal application (Python 3.12+) that makes the classical 4 L / 3 L Water Jug
Problem interactive: play it by hand, inspect the ten textbook production rules,
watch BFS and DFS search the state space, and replay solutions step by step.

Start state `(0,0)` · goal: exactly 2 L in the 4 L jug.

## Install

    python -m venv .venv
    source .venv/bin/activate        # Windows: .venv\Scripts\activate
    pip install -r requirements.txt

## Run

    python main.py                   # interactive menu
    python main.py --no-anim         # menu without animations
    python main.py --solve bfs       # BFS trace, path, metrics (non-interactive)
    python main.py --solve dfs
    python main.py --compare         # BFS vs DFS metrics
    python main.py --validate        # verify the textbook 6-step sequence

## Test

    python -m pytest -v

## Modules (menu)

1. Manual mode — `r1`..`r10`, `r3 2` (discard 2 L), `undo`, `reset`, `rules`, `hint`
2. BFS mode — FIFO queue, visited set, parent links, shortest path
3. DFS mode — stack-based, first solution found (not necessarily shortest)
4. Rule inspector — preconditions/results of all rules on any state you enter
5. State explorer — all reachable states, transitions, dead ends
6. Solution replay — step forward/back or auto-play (BFS, DFS or textbook)
7. Algorithm lab — generated/explored states, max frontier, depth, time, memory
8. Textbook check — verifies the sequence R1, R8, R6, R10, R1, R8

R3/R4 (arbitrary discard) are manual-only; AI search uses the other eight rules,
otherwise it could win instantly by discarding water.

## Layout

    main.py            entry point / CLI flags
    engine/            state.py, rules.py (10 rules), game.py (manual session)
    algorithms/        bfs.py, dfs.py, solver.py (API, verification, state space), metrics.py
    interface/         terminal.py (modes), display.py (Rich renderables), animations.py
    tests/             test_rules.py, test_solver.py

## Not implemented yet (planned)

IDDFS / UCS / A*, custom capacities, challenge mode, NetworkX/Matplotlib graph export,
quizzes, JSON reports.
