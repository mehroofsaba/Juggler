# JUGGLER - Water Jug AI Laboratory

**A terminal-based environment for exploring classical Artificial Intelligence through the Water Jug Problem.**

JUGGLER transforms the well-known 4-litre and 3-litre Water Jug Problem into an interactive AI laboratory built with Python. It combines manual problem-solving, production-rule systems, state-space exploration, and classical search algorithms in one terminal application.

Instead of simply displaying a solution, JUGGLER lets you interact with the problem, understand how its rules work, observe how search algorithms explore possible states, and compare their behaviour through measurable performance metrics.

> **The objective:** Measure exactly 2 litres of water in the 4-litre jug.

---

## Table of Contents

- [The Problem](#the-problem)
- [Project Highlights](#project-highlights)
- [How the Puzzle Works](#how-the-puzzle-works)
- [Production Rule System](#production-rule-system)
- [AI Search Algorithms](#ai-search-algorithms)
- [Application Modes](#application-modes)
- [Installation](#installation)
- [Running JUGGLER](#running-juggler)
- [Command-Line Reference](#command-line-reference)
- [Algorithm Performance Metrics](#algorithm-performance-metrics)
- [Project Architecture](#project-architecture)
- [Testing](#testing)
- [Current Limitations and Future Scope](#current-limitations-and-future-scope)
- [Technologies Used](#technologies-used)

---

## The Problem

The Water Jug Problem is a classical Artificial Intelligence problem used to demonstrate state-space representation, production systems, and problem-solving through search.

JUGGLER uses two unmarked water jugs:

| Jug | Capacity |
|---|---:|
| Jug A | 4 litres |
| Jug B | 3 litres |

**Initial state:** `(0, 0)`

**Goal condition:** `A = 2`

The application represents every configuration as a state:

`(a, b)`

Where:
- `a` represents the amount of water in the 4L jug.
- `b` represents the amount of water in the 3L jug.

A valid state must satisfy:

- `0 ≤ a ≤ 4`
- `0 ≤ b ≤ 3`

The objective is to reach a state where the 4L jug contains exactly 2 litres.

### The textbook solution

One valid sequence of operations is:

```text
(0,0)
   |
   | R1 — Fill the 4L jug
   v
(4,0)
   |
   | R8 — Pour 4L into 3L
   v
(1,3)
   |
   | R6 — Empty the 3L jug
   v
(1,0)
   |
   | R10 — Transfer all water from 4L to 3L
   v
(0,1)
   |
   | R1 — Fill the 4L jug
   v
(4,1)
   |
   | R8 — Pour until the 3L jug is full
   v
(2,3)  ✓ GOAL REACHED
```

This sequence contains six transitions and demonstrates how a sequence of production rules can transform an initial state into a goal state.

---

## Project Highlights

JUGGLER is designed to make classical AI concepts observable and interactive.

- **Manual Problem Solving:** Play the Water Jug Problem using individual production rules.
- **Production Rule Engine:** Inspect and apply ten textbook-inspired operations.
- **Breadth-First Search:** Find a shortest solution using a FIFO queue and visited-state tracking.
- **Depth-First Search:** Explore the state space using a stack-based search strategy.
- **State-Space Exploration:** Discover reachable configurations and their possible transitions.
- **Solution Replay:** Follow solution paths step by step.
- **Algorithm Comparison:** Observe how BFS and DFS differ in their search behaviour.
- **Performance Analysis:** Examine generated states, explored states, frontier size, depth, execution time, and memory usage where supported.
- **Textbook Validation:** Verify the expected six-transition solution against the implemented rule system.

---

## How the Puzzle Works

JUGGLER models the problem as a finite state-space search.

Each state represents a possible distribution of water between the two jugs.

An action applies a valid production rule to the current state and generates a successor state.

The search process continues until the goal condition is satisfied or no further states can be explored.

### State representation

A state is represented as:

```python
(a, b)
```

For example:

```text
(4, 2)
```

means:
- Jug A contains 4 litres.
- Jug B contains 2 litres.

Since the capacities are fixed, there are at most 20 mathematically possible configurations:

`(4 + 1) × (3 + 1) = 20`

Not every possible configuration must be reachable under the selected search operators.

### Goal test

The goal condition is:

```python
a == 2
```

The objective is specifically to obtain exactly 2 litres in the 4L jug.

---

## Production Rule System

JUGGLER implements ten production rules that describe the possible operations on the two jugs.

A production rule consists of:
1. A precondition — when the operation is valid.
2. An action — what happens to the current state.
3. A resulting state — the configuration after applying the operation.

### Rule reference

| Rule | Operation |
|---|---|
| R1 | Fill the 4L jug completely. |
| R2 | Fill the 3L jug completely. |
| R3 | Discard a specified quantity from the 4L jug. |
| R4 | Discard a specified quantity from the 3L jug. |
| R5 | Empty the 4L jug completely. |
| R6 | Empty the 3L jug completely. |
| R7 | Pour water from the 3L jug into the 4L jug until the 4L jug is full or the 3L jug is empty. |
| R8 | Pour water from the 4L jug into the 3L jug until the 3L jug is full or the 4L jug is empty. |
| R9 | Transfer all water from the 3L jug into the 4L jug, provided the total fits. |
| R10 | Transfer all water from the 4L jug into the 3L jug, provided the total fits. |

### Important search-design decision

R3 and R4 allow arbitrary quantities of water to be discarded. If these operations were freely available to the AI search engine, the goal could be reached through an artificial shortcut.

Therefore, JUGGLER separates manual rule interaction from automated search:

- **Manual mode:** All ten rules are available.
- **AI search:** R3 and R4 are excluded; the remaining eight rules are used.

This keeps the search focused on the intended water-transfer problem rather than allowing arbitrary disposal to trivialize the objective.

---

## AI Search Algorithms

JUGGLER demonstrates two fundamental uninformed search strategies.

### 1. Breadth-First Search (BFS)

BFS explores the state space level by level.

It uses a First-In, First-Out (FIFO) queue to process states in the order they are discovered.

**How it works:**

1. Insert the initial state into the queue.
2. Mark the initial state as visited.
3. Remove the next state from the front of the queue.
4. Check whether it satisfies the goal condition.
5. Generate valid successor states using the available production rules.
6. Add previously unvisited states to the queue.
7. Repeat until the goal is found or the queue becomes empty.

**Key characteristics:**
- Explores states level by level.
- Uses a queue and a visited set.
- Stores parent information to reconstruct the solution path.
- Finds a shortest path in terms of transitions when all actions have equal cost.
- Can consume more memory because it retains frontier states.

### 2. Depth-First Search (DFS)

DFS explores one branch of the state space as deeply as possible before backtracking.

It uses a Last-In, First-Out (LIFO) stack.

**How it works:**

1. Push the initial state onto the stack.
2. Mark the initial state as visited.
3. Pop the next state from the stack.
4. Check whether it satisfies the goal condition.
5. Generate valid, unvisited successor states.
6. Push the successors onto the stack.
7. Continue exploring until the goal is found or the stack becomes empty.

**Key characteristics:**
- Explores deeper states before backtracking.
- Uses a stack and a visited set.
- Can find a solution without exploring every possible state.
- Does not guarantee a shortest solution.
- Its behaviour depends on successor ordering.

### BFS vs DFS

| Property | BFS | DFS |
|---|---|---|
| Search strategy | Level by level | Depth first |
| Data structure | Queue | Stack |
| Search type | Uninformed | Uninformed |
| Shortest path | Guaranteed for equal-cost actions | Not guaranteed |
| Memory usage | Can be higher | Often lower, depending on the search |
| Backtracking | Not depth-based | Explicit exploration and backtracking |

Both algorithms operate on the same initial state, goal condition, and automated rule set, making their behaviour suitable for comparison.

---

## Application Modes

JUGGLER brings its AI concepts together through an interactive terminal menu.

### 1. Manual Mode
Solve the puzzle yourself by applying production rules.

Available interactions include:
- Apply rules `r1` through `r10`.
- Specify quantities for discard operations, such as `r3 2`.
- Undo the previous operation.
- Reset the current puzzle.
- Display the rule reference.
- Request a hint.

### 2. BFS Solver
Run Breadth-First Search and inspect its solution trace, path, and performance metrics.

### 3. DFS Solver
Run Depth-First Search and observe how it explores the state space before finding a solution.

### 4. Rule Inspector
Enter a state and inspect the preconditions and resulting states of the available production rules.

### 5. State Explorer
Explore reachable states, their transitions, and states with no available successors.

### 6. Solution Replay
Replay a solution one step at a time or automatically.

Available solution sources:
- BFS
- DFS
- Textbook solution

### 7. Algorithm Lab
Examine search performance through metrics such as:
- Generated states
- Explored states
- Maximum frontier size
- Solution depth
- Execution time
- Memory usage, where measured

### 8. Textbook Validation
Verify the expected six-transition sequence:

```text
R1 → R8 → R6 → R10 → R1 → R8
```

The validation checks the sequence against the implemented state transitions and goal condition.

---

## Installation

### Prerequisites

- Python 3.12 or later
- pip
- VS Code or another code editor (optional)
- Git Bash or Windows PowerShell

### 1. Clone the repository

```bash
git clone https://github.com/mehroofsaba/Juggler.git
```

### 2. Navigate into the project

```bash
cd Juggler
```

### 3. Create a virtual environment

```bash
python -m venv .venv
```

A virtual environment keeps the project's Python dependencies separate from other Python installations.

### 4. Install dependencies

```bash
python -m pip install -r requirements.txt
```

---

## Running JUGGLER

The activation command depends on the terminal you're using.

### Option A — Git Bash (Windows)

Open Git Bash and navigate to the project directory.

If you cloned the project into your Downloads folder:

```bash
cd ~/Downloads/Juggler
```

Create the virtual environment:

```bash
python -m venv .venv
```

Activate it:

```bash
source .venv/Scripts/activate
```

Install dependencies:

```bash
python -m pip install -r requirements.txt
```

Launch the application:

```bash
python main.py
```

### Option B — VS Code Terminal (Windows PowerShell)

Open the project folder in VS Code:

1. Select **File → Open Folder**.
2. Choose the `Juggler` directory.
3. Open the integrated terminal using `Ctrl + ``.
4. Ensure the terminal is running PowerShell.

Navigate to the project directory if necessary:

```powershell
cd "C:\my games collections\Juggler"
```

Create the virtual environment:

```powershell
python -m venv .venv
```

Activate it:

```powershell
.\.venv\Scripts\Activate.ps1
```

If PowerShell blocks activation scripts, allow them for the current terminal session:

```powershell
Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass
```

Then activate again:

```powershell
.\.venv\Scripts\Activate.ps1
```

Install dependencies:

```powershell
python -m pip install -r requirements.txt
```

Launch the application:

```powershell
python main.py
```

**Note:** You only need to create the virtual environment once. When reopening the project, activate the existing environment before running the application.

---

## Command-Line Reference

JUGGLER supports several command-line options for accessing its functionality without navigating the interactive menu.

| Command | Description |
|---|---|
| `python main.py` | Launch the interactive menu. |
| `python main.py --no-anim` | Launch the menu without animations. |
| `python main.py --solve bfs` | Run BFS and display the search trace, solution path, and metrics. |
| `python main.py --solve dfs` | Run DFS and display the search trace, solution path, and metrics. |
| `python main.py --compare` | Compare BFS and DFS performance metrics. |
| `python main.py --validate` | Validate the textbook six-transition solution. |
| `python -m pytest -v` | Execute the test suite with detailed output. |

These commands can be used in either Git Bash or the VS Code PowerShell terminal, provided the virtual environment is activated.

---

## Algorithm Performance Metrics

JUGGLER uses search metrics to make algorithm behaviour easier to observe and compare.

| Metric | Meaning |
|---|---|
| Generated States | Number of states produced during successor generation. |
| Explored States | Number of states processed by the search algorithm. |
| Maximum Frontier | Largest number of pending states held by the queue or stack. |
| Solution Depth | Number of transitions in the discovered solution path. |
| Execution Time | Time taken by the algorithm to complete its search. |
| Memory Usage | Memory consumed during execution, when supported by the implementation. |

The metrics are intended to demonstrate the practical differences between search strategies. Actual values depend on the implementation, successor ordering, and runtime environment.

---

## Project Architecture

JUGGLER follows a modular structure that separates puzzle logic, AI algorithms, and terminal presentation.

```text
Juggler/
│
├── algorithms/
│   ├── __init__.py
│   ├── bfs.py
│   ├── dfs.py
│   ├── metrics.py
│   └── solver.py
│
├── engine/
│   ├── __init__.py
│   ├── game.py
│   ├── rules.py
│   └── state.py
│
├── interface/
│   ├── __init__.py
│   ├── animations.py
│   ├── display.py
│   └── terminal.py
│
├── tests/
│   ├── __init__.py
│   ├── test_rules.py
│   └── test_solver.py
│
├── .gitignore
├── main.py
├── README.md
└── requirements.txt
```

### Module responsibilities

**`engine/` — Puzzle Logic**
- `state.py`: Represents and validates jug configurations.
- `rules.py`: Defines the ten production rules and their transitions.
- `game.py`: Manages manual gameplay and puzzle state.

**`algorithms/` — AI Search**
- `bfs.py`: Implements Breadth-First Search.
- `dfs.py`: Implements Depth-First Search.
- `solver.py`: Coordinates solving, solution verification, and state-space operations.
- `metrics.py`: Collects algorithm performance measurements.

**`interface/` — Terminal Experience**
- `terminal.py`: Handles the interactive application and its modes.
- `display.py`: Renders terminal information and puzzle states.
- `animations.py`: Provides terminal animations.

**`tests/` — Verification**
- `test_rules.py`: Tests production rules and state transitions.
- `test_solver.py`: Tests search and solution behaviour.

**`main.py` — Application Entry Point**

Handles command-line arguments and launches the requested application mode.

---

## Testing

JUGGLER includes automated tests to verify the correctness of its core functionality.

Run the complete test suite:

```bash
python -m pytest -v
```

The tests cover:
- Production rule behaviour.
- Valid state transitions.
- Search algorithm functionality.
- Solution correctness.

Testing helps ensure that the AI engine produces valid state transitions and reaches the intended goal.

---

## Current Limitations and Future Scope

JUGGLER currently focuses on the classical Water Jug Problem and two fundamental uninformed search algorithms.

Potential extensions include:

- **Iterative Deepening DFS (IDDFS):** Combine depth-limited exploration with repeated search.
- **Uniform Cost Search (UCS):** Explore cost-based pathfinding.
- **A* Search:** Introduce heuristic-based search.
- **Custom Jug Capacities:** Allow users to configure different puzzle dimensions.
- **Challenge Mode:** Introduce custom initial states and goal conditions.
- **Algorithm Race:** Compare multiple search algorithms in one experiment.
- **Graph Visualization:** Export state-space graphs using NetworkX and Matplotlib.
- **Interactive Quizzes:** Test understanding of production systems and search strategies.
- **JSON Reports:** Export algorithm traces and performance metrics.

These are planned extensions and are not part of the current implementation.

---

## Technologies Used

| Technology | Purpose |
|---|---|
| Python | Core application and AI logic |
| Rich | Terminal presentation and styling |
| pytest | Automated testing |
| Python Standard Library | Data structures, state management, and utility operations |
| Git & GitHub | Version control and project hosting |

---

## Learning Objectives

JUGGLER is an educational project designed to explore fundamental Artificial Intelligence concepts through implementation.

It demonstrates:

- State-space representation.
- Initial states and goal states.
- Production systems and rule-based problem solving.
- Successor generation.
- Breadth-First Search.
- Depth-First Search.
- Search-tree exploration.
- Path reconstruction.
- Algorithm performance analysis.

The goal is not just to solve the puzzle, but to understand **how an AI system searches for a solution.**

---

**JUGGLER — Every state has a possibility. Every rule changes the game.**
