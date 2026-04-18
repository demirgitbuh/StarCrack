# StarCrack - Hash Cracking Tool
# Usage: python starcrack.py --help
# Requirements: rich (pip install rich)

import argparse
import hashlib
import itertools
import json
import os
import string
import sys
import time
from datetime import datetime

try:
    sys.stdout.reconfigure(encoding="utf-8")
except Exception:
    pass

from rich.console import Console
from rich.panel import Panel
from rich.live import Live
from rich.table import Table
from rich.progress import Progress, SpinnerColumn, BarColumn, TextColumn, TimeElapsedColumn
from rich.text import Text
from rich.prompt import Prompt, IntPrompt
from rich.align import Align
from rich.rule import Rule
from rich.columns import Columns
from rich.padding import Padding

VERSION = "0.1.0"
DATA_DIR = "./data"
RESULTS_FILE = os.path.join(DATA_DIR, "results.txt")

HASH_TYPES = {
    32: "md5",
    40: "sha1",
    64: "sha256",
    128: "sha512",
}

CHARSETS = {
    "lowercase": string.ascii_lowercase,
    "uppercase": string.ascii_uppercase,
    "digits": string.digits,
    "symbols": string.punctuation,
    "all": string.ascii_letters + string.digits + string.punctuation,
}


def detect_hash_type(hash_str: str) -> str:
    """Detect hash algorithm from hash length."""
    return HASH_TYPES.get(len(hash_str.strip()), "unknown")


def hash_word(word: str, algo: str) -> str:
    """Hash a word with the given algorithm and return hex digest."""
    h = hashlib.new(algo)
    h.update(word.encode("utf-8", errors="ignore"))
    return h.hexdigest()


def _make_progress() -> Progress:
    """Build a styled Rich progress instance."""
    return Progress(
        SpinnerColumn(spinner_name="line", style="bright_blue"),
        TextColumn("[grey70]{task.description}"),
        BarColumn(bar_width=30, complete_style="bright_blue", finished_style="green"),
        TextColumn("[blue]{task.percentage:>5.1f}%"),
        TextColumn("[grey50]•"),
        TextColumn("[grey70]{task.fields[current]}"),
        TextColumn("[grey50]•"),
        TextColumn("[blue]{task.fields[rate]:.0f} h/s"),
        TextColumn("[grey50]•"),
        TextColumn("[grey70]{task.completed} tries"),
        TimeElapsedColumn(),
    )


def dict_attack(target_hash: str, algo: str, wordlist: str, console: Console) -> dict:
    """Run a dictionary attack by hashing each line of the wordlist."""
    target = target_hash.lower().strip()
    start = time.time()
    attempts = 0
    found = None
    last_word = ""

    try:
        total = sum(1 for _ in open(wordlist, "rb"))
    except OSError as e:
        console.print(Panel(f"[red]Cannot read wordlist:[/red] {e}", border_style="red"))
        return {"result": "error", "plaintext": None, "attempts": 0, "duration": 0}

    progress = _make_progress()
    task = progress.add_task("Dictionary", total=total, current="", rate=0.0)

    with Live(progress, console=console, refresh_per_second=12):
        try:
            with open(wordlist, "r", encoding="utf-8", errors="ignore") as f:
                for line in f:
                    word = line.rstrip("\n\r")
                    attempts += 1
                    last_word = word
                    if hash_word(word, algo) == target:
                        found = word
                        progress.update(task, advance=1, current=word[:20],
                                        rate=attempts / max(time.time() - start, 1e-6))
                        break
                    if attempts % 500 == 0:
                        elapsed = max(time.time() - start, 1e-6)
                        progress.update(task, advance=500, current=word[:20],
                                        rate=attempts / elapsed)
                    else:
                        progress.advance(task, 0)
        except KeyboardInterrupt:
            raise

    duration = time.time() - start
    return {
        "result": "cracked" if found else "not_found",
        "plaintext": found,
        "attempts": attempts,
        "duration": duration,
        "last_attempt": last_word,
    }


def brute_attack(target_hash: str, algo: str, charset_name: str, maxlen: int, console: Console) -> dict:
    """Run a brute-force attack over a charset up to a maximum length."""
    target = target_hash.lower().strip()
    chars = CHARSETS.get(charset_name)
    if not chars:
        console.print(Panel(f"[red]Unknown charset:[/red] {charset_name}", border_style="red"))
        return {"result": "error", "plaintext": None, "attempts": 0, "duration": 0}

    total = sum(len(chars) ** n for n in range(1, maxlen + 1))
    start = time.time()
    attempts = 0
    found = None
    last_word = ""

    progress = _make_progress()
    task = progress.add_task("Brute-force", total=total, current="", rate=0.0)

    with Live(progress, console=console, refresh_per_second=12):
        try:
            for length in range(1, maxlen + 1):
                for combo in itertools.product(chars, repeat=length):
                    word = "".join(combo)
                    attempts += 1
                    last_word = word
                    if hash_word(word, algo) == target:
                        found = word
                        progress.update(task, advance=1, current=word,
                                        rate=attempts / max(time.time() - start, 1e-6))
                        break
                    if attempts % 1000 == 0:
                        elapsed = max(time.time() - start, 1e-6)
                        progress.update(task, advance=1000, current=word,
                                        rate=attempts / elapsed)
                if found:
                    break
        except KeyboardInterrupt:
            raise

    duration = time.time() - start
    return {
        "result": "cracked" if found else "not_found",
        "plaintext": found,
        "attempts": attempts,
        "duration": duration,
        "last_attempt": last_word,
    }


def save_result(data: dict, json_path: str = None) -> None:
    """Append a one-line summary to results.txt and optionally write a JSON report."""
    os.makedirs(DATA_DIR, exist_ok=True)
    ts = data.get("timestamp") or datetime.now().isoformat(timespec="seconds")
    line = (
        f"[{ts}] {data.get('hash','')} | {data.get('hash_type','')} | "
        f"{data.get('mode','')} | {data.get('result','')}"
    )
    if data.get("plaintext"):
        line += f" | {data['plaintext']}"
    with open(RESULTS_FILE, "a", encoding="utf-8") as f:
        f.write(line + "\n")

    if json_path:
        with open(json_path, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2)


def build_info_panel(target: str, algo: str, mode: str, wordlist: str,
                     charset: str, maxlen: int) -> Panel:
    """Build the info panel describing the current run parameters."""
    table = Table.grid(padding=(0, 2), expand=True)
    table.add_column(style="grey50", width=3)
    table.add_column(style="grey70", width=14)
    table.add_column(style="bright_blue bold")

    display_hash = target if len(target) <= 56 else target[:53] + "..."
    table.add_row("▸", "target hash", display_hash)
    table.add_row("▸", "algorithm", algo.upper())
    table.add_row("▸", "mode", mode)
    if mode == "dict":
        table.add_row("▸", "wordlist", wordlist or "-")
    else:
        table.add_row("▸", "charset", charset or "-")
        table.add_row("▸", "max length", str(maxlen))
    return Panel(Padding(table, (1, 1)),
                 title="[bright_blue]◆ Configuration[/bright_blue]",
                 border_style="blue", title_align="left")


def build_header() -> Panel:
    """Build the modern startup/header panel."""
    now = datetime.now().strftime("%Y-%m-%d  %H:%M:%S")
    title = Text()
    title.append("◆ ", style="bright_blue")
    title.append("StarCrack", style="bold bright_blue")
    title.append(f"  v{VERSION}", style="grey50")
    subtitle = Text("Hash Cracking Tool", style="italic grey70")
    meta = Text(now, style="grey50")

    body = Table.grid(expand=True)
    body.add_column(justify="center")
    body.add_row(title)
    body.add_row(subtitle)
    body.add_row(Rule(style="blue"))
    body.add_row(meta)
    return Panel(Padding(body, (0, 2)), border_style="bright_blue", padding=(0, 0))


def build_result_panel(result: dict) -> Panel:
    """Build the final result panel."""
    grid = Table.grid(expand=True)
    grid.add_column(justify="center")
    rate = result["attempts"] / max(result["duration"], 1e-6)

    if result["result"] == "cracked":
        status = Text("✓  CRACKED", style="bold green")
        grid.add_row(status)
        grid.add_row(Rule(style="green"))
        pt = Text()
        pt.append("plaintext  ", style="grey70")
        pt.append(str(result["plaintext"]), style="bold bright_blue")
        grid.add_row(pt)
        stats = Text(
            f"{result['attempts']:,} tries   •   {result['duration']:.2f}s   •   {rate:,.0f} h/s",
            style="grey50",
        )
        grid.add_row(stats)
        return Panel(Padding(grid, (1, 2)), border_style="green",
                     title="[green]◆ Result[/green]", title_align="left")

    if result["result"] == "not_found":
        status = Text("✗  NOT FOUND", style="bold red")
        grid.add_row(status)
        grid.add_row(Rule(style="red"))
        stats = Text(
            f"{result['attempts']:,} tries   •   {result['duration']:.2f}s   •   {rate:,.0f} h/s",
            style="grey50",
        )
        grid.add_row(stats)
        return Panel(Padding(grid, (1, 2)), border_style="red",
                     title="[red]◆ Result[/red]", title_align="left")

    return Panel(Padding(Text("Error during attack", style="bold red"), (1, 2)),
                 border_style="red", title="[red]◆ Result[/red]", title_align="left")


def build_menu_panel() -> Panel:
    """Build the main menu panel with attack options."""
    table = Table.grid(padding=(0, 2), expand=True)
    table.add_column(style="bright_blue bold", justify="center", width=4)
    table.add_column(style="grey70", width=3)
    table.add_column(style="bright_blue bold")
    table.add_column(style="grey50", justify="right")
    table.add_row("1", "›", "Dictionary Attack", "wordlist")
    table.add_row("2", "›", "Brute-force Attack", "itertools")
    table.add_row("3", "›", "View Last Results", "./data")
    table.add_row("q", "›", "Quit", "exit")
    return Panel(Padding(table, (1, 2)),
                 title="[bright_blue]◆ Main Menu[/bright_blue]",
                 subtitle="[grey50]select an action[/grey50]",
                 border_style="blue", title_align="left")


def prompt_hash(console: Console) -> str:
    """Prompt the user for a target hash until a valid one is entered."""
    while True:
        h = Prompt.ask("[bright_blue]Target hash[/bright_blue]", console=console).strip().lower()
        if not h:
            console.print("[red]Hash cannot be empty.[/red]")
            continue
        if detect_hash_type(h) == "unknown":
            console.print("[red]Unrecognized hash length. "
                          "Expected 32/40/64/128 hex chars.[/red]")
            continue
        return h


def view_results(console: Console) -> None:
    """Display the last lines of the results log."""
    if not os.path.isfile(RESULTS_FILE):
        console.print(Panel("[grey70]No results logged yet.[/grey70]", border_style="grey50"))
        return
    with open(RESULTS_FILE, "r", encoding="utf-8") as f:
        lines = f.readlines()[-15:]
    body = Text("".join(lines) if lines else "(empty)", style="grey70")
    console.print(Panel(body, title="[blue]Recent Results[/blue]",
                        border_style="blue", title_align="left"))


def run_attack(console: Console, mode: str, target: str, algo: str,
               wordlist: str = None, charset: str = "lowercase",
               maxlen: int = 4, output: str = None) -> None:
    """Execute an attack and render the result panel + persist output."""
    console.print(build_info_panel(target, algo, mode, wordlist, charset, maxlen))
    started_ts = datetime.now().isoformat(timespec="seconds")
    result = {"result": "error", "plaintext": None, "attempts": 0, "duration": 0}
    try:
        if mode == "dict":
            result = dict_attack(target, algo, wordlist, console)
        else:
            result = brute_attack(target, algo, charset, maxlen, console)
    except KeyboardInterrupt:
        console.print("\n[yellow]Interrupted by user.[/yellow]")
        result["result"] = "interrupted"

    display = result if result["result"] in ("cracked", "not_found") \
        else {**result, "result": "not_found"}
    console.print(build_result_panel(display))

    record = {
        "hash": target,
        "hash_type": algo,
        "mode": mode,
        "result": result["result"],
        "plaintext": result.get("plaintext"),
        "attempts": result.get("attempts", 0),
        "duration": round(result.get("duration", 0), 4),
        "timestamp": started_ts,
    }
    save_result(record, output)


def interactive_tui(console: Console) -> None:
    """Run the interactive menu-driven TUI loop."""
    while True:
        console.print(build_menu_panel())
        choice = Prompt.ask("[bright_blue]Choose[/bright_blue]",
                            choices=["1", "2", "3", "q"], default="1",
                            console=console)

        if choice == "q":
            console.print("[grey70]Bye.[/grey70]")
            return

        if choice == "3":
            view_results(console)
            continue

        target = prompt_hash(console)
        algo = detect_hash_type(target)
        console.print(f"[grey70]Detected:[/grey70] [bright_blue]{algo.upper()}[/bright_blue]")

        save_json = Prompt.ask("[bright_blue]Export JSON report? (path or empty)[/bright_blue]",
                               default="", console=console).strip() or None

        if choice == "1":
            wl = Prompt.ask("[bright_blue]Wordlist path[/bright_blue]", console=console).strip()
            if not os.path.isfile(wl):
                console.print(f"[red]Wordlist not found:[/red] {wl}")
                continue
            run_attack(console, "dict", target, algo, wordlist=wl, output=save_json)
        else:
            cs = Prompt.ask("[bright_blue]Charset[/bright_blue]",
                            choices=list(CHARSETS.keys()), default="lowercase",
                            console=console)
            ml = IntPrompt.ask("[bright_blue]Max length[/bright_blue]", default=4, console=console)
            run_attack(console, "brute", target, algo, charset=cs, maxlen=ml, output=save_json)


def main() -> None:
    """Parse CLI args, run the selected attack, and display/save results."""
    parser = argparse.ArgumentParser(
        prog="starcrack",
        description="StarCrack - Hash Cracking Tool",
        add_help=False,
    )
    parser.add_argument("--help", action="help", help="Show this help message and exit")
    parser.add_argument("-H", "--hash", dest="hash", help="Target hash")
    parser.add_argument("-h", dest="hash_short", help="Target hash (short form)")
    parser.add_argument("-m", "--mode", choices=["dict", "brute"], help="Attack mode")
    parser.add_argument("-w", "--wordlist", help="Wordlist path (dict mode)")
    parser.add_argument("-c", "--charset", default="lowercase",
                        choices=list(CHARSETS.keys()), help="Charset (brute mode)")
    parser.add_argument("-l", "--maxlen", type=int, default=4, help="Max length (brute mode)")
    parser.add_argument("-a", "--algo", choices=["md5", "sha1", "sha256", "sha512"],
                        help="Override hash algorithm")
    parser.add_argument("-o", "--output", help="JSON report output path")

    args = parser.parse_args()

    console = Console()
    os.makedirs(DATA_DIR, exist_ok=True)

    console.print(build_header())

    target = args.hash or args.hash_short

    if not target and not args.mode:
        try:
            interactive_tui(console)
        except KeyboardInterrupt:
            console.print("\n[grey70]Bye.[/grey70]")
        return

    if not target or not args.mode:
        console.print("[red]Missing required arguments.[/red] Run with --help "
                      "or no args for interactive TUI.")
        sys.exit(1)
    target = target.strip().lower()

    algo = args.algo or detect_hash_type(target)
    if algo == "unknown":
        console.print(Panel("[red]Unable to detect hash type from length. "
                            "Use -a to specify.[/red]", border_style="red"))
        sys.exit(1)

    if args.mode == "dict":
        if not args.wordlist or not os.path.isfile(args.wordlist):
            console.print(f"[red]Wordlist missing or not found:[/red] {args.wordlist}")
            sys.exit(1)
        run_attack(console, "dict", target, algo,
                   wordlist=args.wordlist, output=args.output)
    else:
        run_attack(console, "brute", target, algo,
                   charset=args.charset, maxlen=args.maxlen, output=args.output)


if __name__ == "__main__":
    main()
