#!/usr/bin/env python3
"""JUGGLER - interactive terminal laboratory for the Water Jug Problem.

Usage:
    python main.py                 interactive menu
    python main.py --solve bfs     print a BFS solution and exit
    python main.py --solve dfs     print a DFS solution and exit
    python main.py --compare       BFS vs DFS metrics table and exit
    python main.py --validate      verify the textbook sequence and exit
    python main.py --no-anim       interactive menu without animations
"""
import argparse
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

try:
    from rich.console import Console
except ImportError:
    sys.exit("Rich is not installed. Run:  pip install -r requirements.txt")

from algorithms.solver import compare, solve, validate_textbook, verify_path
from interface import display
from interface.terminal import App


def main() -> int:
    p = argparse.ArgumentParser(description="JUGGLER - Water Jug AI laboratory")
    p.add_argument("--solve", choices=["bfs", "dfs"], help="run a search and print the result")
    p.add_argument("--compare", action="store_true", help="compare BFS and DFS")
    p.add_argument("--validate", action="store_true", help="verify the textbook solution")
    p.add_argument("--no-anim", action="store_true", help="disable animations")
    args = p.parse_args()

    console = Console()
    app = App(console, animate=not args.no_anim)

    if args.solve:
        res = solve(args.solve)
        verify_path(res.path, res.rules)
        console.print(display.trace_table(res))
        console.print(display.path_table(res))
        console.print(display.metrics_table([res]))
        return 0 if res.found else 1
    if args.compare:
        console.print(display.metrics_table(compare()))
        return 0
    if args.validate:
        app.textbook()
        return 0

    app.run()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
