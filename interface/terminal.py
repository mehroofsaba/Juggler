"""Interactive terminal application: menu and the eight modes."""
from __future__ import annotations

from rich.console import Console
from rich.panel import Panel
from rich.prompt import Prompt
from rich.text import Text

from algorithms.solver import (TEXTBOOK_RULES, TEXTBOOK_STATES, compare, solve,
                               state_space, validate_textbook, verify_path)
from engine.game import Game
from engine.rules import RULES_BY_ID, RuleError, get_rule
from engine.state import INITIAL, State

from . import animations, display

MENU = [
    ("1", "MANUAL MODE", "Play the puzzle with the production rules"),
    ("2", "BFS MODE", "Find the shortest solution"),
    ("3", "DFS MODE", "Explore the possibilities depth-first"),
    ("4", "RULE INSPECTOR", "Understand the ten rules, test them on any state"),
    ("5", "STATE EXPLORER", "Discover the whole reachable state space"),
    ("6", "SOLUTION REPLAY", "Step through a solution at your own pace"),
    ("7", "ALGORITHM LAB", "Compare BFS and DFS with real metrics"),
    ("8", "TEXTBOOK CHECK", "Verify the textbook's 6-step sequence"),
    ("q", "QUIT", ""),
]


class App:
    def __init__(self, console: Console | None = None, animate: bool = True) -> None:
        self.console = console or Console()
        self.animate = animate

    # ---- shell -----------------------------------------------------------
    def ask(self, prompt: str) -> str:
        try:
            return Prompt.ask(f"[cyan]{prompt}[/cyan]", console=self.console).strip()
        except (EOFError, KeyboardInterrupt):
            return "q"

    def run(self) -> None:
        self.console.clear()
        self.console.print(display.banner())
        while True:
            self.console.print(self.menu_panel())
            choice = self.ask("select module").lower()
            actions = {"1": self.manual, "2": lambda: self.search("bfs"), "3": lambda: self.search("dfs"),
                       "4": self.inspector, "5": self.explorer, "6": self.replay,
                       "7": self.lab, "8": self.textbook}
            if choice in ("q", "quit", "exit"):
                self.console.print("[grey62]Session closed. One state at a time.[/grey62]")
                return
            if choice in actions:
                try:
                    actions[choice]()
                except (KeyboardInterrupt, EOFError):
                    self.console.print("\n[yellow]Interrupted - back to menu.[/yellow]")
            else:
                self.console.print(f"[red]Unknown option '{choice}'.[/red]")

    def menu_panel(self) -> Panel:
        t = Text()
        for key, name, desc in MENU:
            t.append(f" [{key}] ", style="bold cyan")
            t.append(f"{name:<16}", style="bold white")
            t.append(f"{desc}\n", style="grey62")
        return Panel(t, title="MODULES", border_style=display.BLUE)

    # ---- 1. manual -------------------------------------------------------
    def manual(self) -> None:
        game = Game()
        self.console.print(Panel(
            "Commands: [cyan]r1..r10[/cyan] apply a rule (R3/R4 need an amount: [cyan]r3 2[/cyan])  ·  "
            "[cyan]undo[/cyan]  ·  [cyan]reset[/cyan]  ·  [cyan]rules[/cyan]  ·  [cyan]hint[/cyan]  ·  [cyan]q[/cyan] back\n"
            "Goal: exactly 2 L in the 4 L jug.", title="MANUAL MODE", border_style=display.BLUE))
        self.console.print(display.jugs_panel(game.state.i, game.state.j))
        while True:
            cmd = self.ask(f"[moves: {game.moves}] rule").lower().split()
            if not cmd:
                continue
            word = cmd[0]
            if word in ("q", "quit", "menu", "back"):
                return
            if word == "rules":
                self.console.print(display.rules_table())
            elif word == "reset":
                game.reset()
                self.console.print(display.jugs_panel(game.state.i, game.state.j, subtitle="reset"))
            elif word == "undo":
                move = game.undo()
                if move is None:
                    self.console.print("[yellow]Nothing to undo.[/yellow]")
                else:
                    self.console.print(display.jugs_panel(game.state.i, game.state.j, subtitle="undone"))
            elif word == "hint":
                self.hint(game)
            else:
                self.manual_move(game, cmd)

    def manual_move(self, game: Game, cmd: list[str]) -> None:
        try:
            amount = int(cmd[1]) if len(cmd) > 1 else None
        except ValueError:
            self.console.print("[red]The amount must be a whole number.[/red]")
            return
        try:
            rule = get_rule(cmd[0])
            if rule.needs_amount and amount is None:
                amount = int(self.ask("litres to discard") or "0")
            move = game.apply(rule.id, amount)
        except KeyError as e:
            self.console.print(f"[red]{e.args[0]}[/red]")
            return
        except ValueError:
            self.console.print("[red]The amount must be a whole number.[/red]")
            return
        except RuleError as e:
            self.console.print(f"[red]Invalid move:[/red] {e}")
            return
        self.console.print(display.move_line(move.rule, move.before, move.after, move.amount))
        animations.pour(self.console, move.before, move.after,
                        label=f"{move.rule.id} · move {game.moves}", enabled=self.animate)
        if game.won:
            self.console.print(Panel(f"Goal reached in {game.moves} move(s): exactly 2 L in the 4 L jug.\n"
                                     "The shortest possible solution takes 6 moves. Type 'reset' to try again.",
                                     border_style=display.GREEN, title="SOLVED"))

    def hint(self, game: Game) -> None:
        res = solve("bfs", game.state, game.goal, measure_memory=False)
        if game.won:
            self.console.print("[green]You are already at the goal.[/green]")
        elif not res.found:
            self.console.print("[yellow]No AI-reachable solution from here (try 'undo' or 'reset').[/yellow]")
        else:
            rid = res.rules[0]
            self.console.print(f"BFS suggests [bold cyan]{rid}[/bold cyan] ({RULES_BY_ID[rid].name}) → "
                               f"{res.path[1]}; {res.path_length} move(s) remain at best.")

    # ---- 2/3. BFS and DFS -------------------------------------------------
    def search(self, name: str) -> None:
        animations.thinking(self.console, f"running {name.upper()}...", self.animate)
        res = solve(name)
        self.console.print(display.trace_table(res))
        if not res.found:
            self.console.print("[red]No solution found.[/red]")
            return
        verify_path(res.path, res.rules)          # independent legality check
        self.console.print(display.path_table(res))
        self.console.print(display.metrics_table([res]))
        note = ("BFS guarantees the shortest path when every transition costs the same."
                if name == "bfs" else
                "DFS returns the first solution it meets; it does not guarantee the shortest path. "
                "Compare it with BFS in the Algorithm Lab.")
        self.console.print(f"[grey62]{note}  Path verified rule-by-rule ✓[/grey62]")
        if self.ask("replay this solution step by step? (y/N)").lower() == "y":
            self.play_steps(res.path, res.rules, res.algorithm)

    # ---- 4. inspector -----------------------------------------------------
    def inspector(self) -> None:
        self.console.print(display.rules_table())
        self.console.print("[grey62]R3/R4 discard arbitrary amounts, so the AI search never uses them.[/grey62]")
        while True:
            raw = self.ask("test a state, e.g. 2,3 (blank to go back)")
            if raw.lower() in ("", "q", "back"):
                return
            try:
                state = State.parse(raw)
            except ValueError as e:
                self.console.print(f"[red]{e}[/red]")
                continue
            self.console.print(display.jugs_panel(state.i, state.j))
            self.console.print(display.rule_check_table(state))

    # ---- 5. state explorer -----------------------------------------------
    def explorer(self) -> None:
        ss = state_space()
        self.console.print(display.state_space_table(ss))
        self.console.print(Panel(
            f"{len(ss.states)} reachable states of 20 possible pairs  ·  {len(ss.edges)} transitions\n"
            f"Goal states: {', '.join(map(str, ss.goal_states))}\n"
            f"Dead ends (goal unreachable): {', '.join(map(str, ss.dead_ends)) or 'none'}",
            title="STATE SPACE", border_style=display.BLUE))
        while True:
            raw = self.ask("inspect a state, e.g. 4,1 (blank to go back)")
            if raw.lower() in ("", "q", "back"):
                return
            try:
                s = State.parse(raw)
            except ValueError as e:
                self.console.print(f"[red]{e}[/red]")
                continue
            if s not in ss.levels:
                self.console.print(f"[yellow]{s} is not reachable from (0,0).[/yellow]")
                continue
            outs = [f"{rid}→{b}" for a, rid, b in ss.edges if a == s]
            ins = [f"{a} via {rid}" for a, rid, b in ss.edges if b == s]
            self.console.print(display.jugs_panel(s.i, s.j, subtitle=f"BFS level {ss.levels[s]}"))
            self.console.print(f"Outgoing: {'  '.join(outs) or '-'}\nIncoming: {'  ; '.join(ins) or '-'}")

    # ---- 6. replay ---------------------------------------------------------
    def replay(self) -> None:
        pick = self.ask("replay which solution? [1] BFS  [2] DFS  [3] textbook").strip()
        if pick == "3":
            self.play_steps(TEXTBOOK_STATES, TEXTBOOK_RULES, "TEXTBOOK")
        elif pick in ("1", "2"):
            res = solve("bfs" if pick == "1" else "dfs", measure_memory=False)
            self.play_steps(res.path, res.rules, res.algorithm)
        else:
            self.console.print("[yellow]Cancelled.[/yellow]")

    def play_steps(self, path: list[State], rules: list[str], label: str) -> None:
        verify_path(path, rules)
        k = 0
        total = len(rules)
        while True:
            self.console.print(display.jugs_panel(path[k].i, path[k].j,
                                                  title=f"{label} · step {k}/{total}"))
            if k < total:
                r = RULES_BY_ID[rules[k]]
                self.console.print(f"Next: [cyan]{r.id}[/cyan] {r.name}  {r.formula}  →  {path[k + 1]}")
            if k > 0:
                self.console.print(f"Previous: {path[k - 1]} via {rules[k - 1]}")
            cmd = self.ask("[Enter] next  [b] back  [a] auto-play  [q] quit").lower()
            if cmd == "q":
                return
            if cmd == "b":
                k = max(k - 1, 0)
            elif cmd == "a":
                while k < total:
                    animations.pour(self.console, path[k], path[k + 1], f"{rules[k]}", self.animate, 0.18)
                    k += 1
                self.console.print("[green]Replay finished.[/green]")
                return
            else:
                if k >= total:
                    self.console.print("[green]Replay finished.[/green]")
                    return
                animations.pour(self.console, path[k], path[k + 1], f"{rules[k]}", self.animate)
                k += 1

    # ---- 7. lab ------------------------------------------------------------
    def lab(self) -> None:
        animations.thinking(self.console, "benchmarking...", self.animate)
        results = compare()
        self.console.print(display.metrics_table(results))
        by = {r.algorithm: r for r in results}
        b, d = by["BFS"], by["DFS"]
        self.console.print(
            f"BFS path: {b.path_length} transitions (shortest). DFS path: {d.path_length} transitions "
            f"({'same length' if d.path_length == b.path_length else 'not the shortest'}).\n"
            "[grey62]Times are wall-clock measurements on this machine; they vary between runs.[/grey62]")
        for r in results:
            self.console.print(f"{r.algorithm}: " + " → ".join(map(str, r.path)))

    # ---- 8. textbook -------------------------------------------------------
    def textbook(self) -> None:
        try:
            steps = validate_textbook()
        except AssertionError as e:
            self.console.print(f"[red]Textbook validation FAILED: {e}[/red]")
            return
        for n, (rid, a, b) in enumerate(steps, start=1):
            self.console.print(f"{n}. " , display.move_line(RULES_BY_ID[rid], a, b))
        self.console.print(Panel("All 6 transitions are produced by their rules and the final state satisfies i = 2.",
                                 border_style=display.GREEN, title="TEXTBOOK SEQUENCE VERIFIED"))
