#!/usr/bin/env python3
"""Math Facts Trainer: Addition & Subtraction within 20

Vibe coded with Claude Code with planning by Robert Dowden

Practice addition and subtraction facts with 4 games:
  1  Practice    — one retry per problem
  2  Drill       — unlimited retries until correct
  3  Flashcards  — reveal the answer if you're wrong
  4  Quiz        — multiple choice
"""

import random

# ANSI colors
GREEN  = '\033[92m'
RED    = '\033[91m'
YELLOW = '\033[93m'
CYAN   = '\033[96m'
BOLD   = '\033[1m'
RESET  = '\033[0m'

def green(t):  return f"{GREEN}{t}{RESET}"
def red(t):    return f"{RED}{t}{RESET}"
def yellow(t): return f"{YELLOW}{t}{RESET}"
def cyan(t):   return f"{CYAN}{t}{RESET}"
def bold(t):   return f"{BOLD}{t}{RESET}"

def styled_q(q):
    """Bold the question; make + bold-green and - bold-red."""
    q = q.replace('+', f"{BOLD}{GREEN}+{RESET}{BOLD}")
    q = q.replace('-', f"{BOLD}{RED}-{RESET}{BOLD}")
    return f"{BOLD}{q}{RESET}"

QUIT = object()  # sentinel
FLIP = object()  # sentinel — player wants to see the answer


# ---------------------------------------------------------------------------
# Problem generation
# ---------------------------------------------------------------------------

def generate_problems():
    """Return addition/subtraction facts where all values stay within 0-20.

    Addition  (x + y = z, z <= 20): blank can be x, y, or z.
    Subtraction (x - y = z, x <= 20, y <= x): blank can be x, y, or z.
    """
    raw = []

    # Addition: x + y = z, z <= 20
    for x in range(21):
        for y in range(21 - x):
            z = x + y
            raw.append({'q': f"{x} + {y} = ___", 'a': z})
            raw.append({'q': f"{x} + ___ = {z}", 'a': y})
            raw.append({'q': f"___ + {y} = {z}", 'a': x})

    # Subtraction: x - y = z, x <= 20, y <= x
    for x in range(21):
        for y in range(x + 1):
            z = x - y
            raw.append({'q': f"{x} - {y} = ___", 'a': z})
            raw.append({'q': f"{x} - ___ = {z}", 'a': y})
            raw.append({'q': f"___ - {y} = {z}", 'a': x})

    # Deduplicate by (question, answer)
    seen, unique = set(), []
    for p in raw:
        key = (p['q'], p['a'])
        if key not in seen:
            seen.add(key)
            unique.append(p)
    return unique


# ---------------------------------------------------------------------------
# Input helpers
# ---------------------------------------------------------------------------

def get_answer(prompt="  Answer: "):
    """Prompt for an integer. Returns the int, or QUIT on 'q'/Ctrl-C."""
    while True:
        try:
            raw = input(prompt).strip()
        except (EOFError, KeyboardInterrupt):
            print()
            return QUIT
        if raw.lower() in ('q', 'quit', 'exit'):
            return QUIT
        try:
            return int(raw)
        except ValueError:
            print(red("  Please enter a number (or 'q' to quit)."))


def get_answer_or_flip(prompt="  Try again or press Enter to flip the card: "):
    """Like get_answer but returns FLIP on bare Enter."""
    while True:
        try:
            raw = input(prompt).strip()
        except (EOFError, KeyboardInterrupt):
            print()
            return QUIT
        if raw.lower() in ('q', 'quit', 'exit'):
            return QUIT
        if raw == '':
            return FLIP
        try:
            return int(raw)
        except ValueError:
            print(red("  Please enter a number, press Enter to flip, or 'q' to quit."))


# ---------------------------------------------------------------------------
# Scoring
# ---------------------------------------------------------------------------

def show_score(correct, total, label="Score"):
    if total == 0:
        return
    pct = int(correct / total * 100)
    color = green if pct >= 80 else yellow if pct >= 60 else red
    print(f"\n  {label}: {color(f'{correct}/{total} ({pct}%)')}")


# ---------------------------------------------------------------------------
# Game 1 — One retry per problem
# ---------------------------------------------------------------------------

def game_1(problems):
    correct = attempted = 0
    for i, p in enumerate(problems):
        print(f"\n[{i+1}/{len(problems)}]  {styled_q(p['q'])}")

        ans = get_answer()
        if ans is QUIT:
            break
        attempted += 1

        if ans == p['a']:
            print(green("  Correct!"))
            correct += 1
        else:
            print(yellow("  Not quite — one more try!"))
            ans2 = get_answer()
            if ans2 is QUIT:
                break
            if ans2 == p['a']:
                print(green("  Correct!"))
                correct += 1
            else:
                print(red(f"  The answer is {p['a']}."))

    show_score(correct, attempted)


# ---------------------------------------------------------------------------
# Game 2 — Unlimited retries
# ---------------------------------------------------------------------------

def game_2(problems):
    first_try_correct = completed = 0

    for i, p in enumerate(problems):
        print(f"\n[{i+1}/{len(problems)}]  {styled_q(p['q'])}")
        first_try = True

        while True:
            ans = get_answer()
            if ans is QUIT:
                show_score(first_try_correct, completed, label="First-try score")
                return

            if ans == p['a']:
                print(green("  Correct!"))
                if first_try:
                    first_try_correct += 1
                completed += 1
                break
            else:
                print(red("  Not quite — try again!"))
                first_try = False

    show_score(first_try_correct, completed, label="First-try score")


# ---------------------------------------------------------------------------
# Game 3 — Flashcard (reveal answer on wrong)
# ---------------------------------------------------------------------------

def game_3(problems):
    correct = attempted = 0

    for i, p in enumerate(problems):
        print(f"\n[{i+1}/{len(problems)}]  {styled_q(p['q'])}")

        ans = get_answer()
        if ans is QUIT:
            break
        attempted += 1

        if ans == p['a']:
            print(green("  Correct!"))
            correct += 1
            continue

        # First attempt was wrong — let the player retry or flip
        print(red("  Incorrect."))
        while True:
            retry = get_answer_or_flip()
            if retry is QUIT:
                show_score(correct, attempted)
                return
            if retry is FLIP:
                print(cyan(f"  Answer: {p['a']}"))
                break
            if retry == p['a']:
                print(green("  Correct!"))
                break
            print(red("  Not quite."))

    show_score(correct, attempted)


# ---------------------------------------------------------------------------
# Game 4 — Multiple choice
# ---------------------------------------------------------------------------

def build_choices(answer, count=4):
    """Build `count` distinct choices that include the correct answer."""
    pool = {answer}
    # Try nearby values first
    nearby = list(range(max(0, answer - 5), min(21, answer + 6)))
    random.shuffle(nearby)
    for c in nearby:
        if c != answer:
            pool.add(c)
        if len(pool) == count:
            break
    # Fall back to any valid answer
    for c in range(21):
        if len(pool) == count:
            break
        pool.add(c)
    choices = list(pool)
    random.shuffle(choices)
    return choices


def game_4(problems):
    correct = attempted = 0

    for i, p in enumerate(problems):
        print(f"\n[{i+1}/{len(problems)}]  {styled_q(p['q'])}")

        choices = build_choices(p['a'])
        for j, c in enumerate(choices):
            print(f"    {j+1}.  {c}")

        while True:
            sel = get_answer("  Choose (1-4): ")
            if sel is QUIT:
                show_score(correct, attempted)
                return
            if 1 <= sel <= 4:
                break
            print(red("  Please enter 1, 2, 3, or 4."))

        attempted += 1
        if choices[sel - 1] == p['a']:
            print(green("  Correct!"))
            correct += 1
        else:
            print(red(f"  Incorrect. The answer is {p['a']}."))

    show_score(correct, attempted)


# ---------------------------------------------------------------------------
# Main menu
# ---------------------------------------------------------------------------

GAMES = {
    '1': ('Practice    (one retry per problem)',   game_1),
    '2': ('Drill       (unlimited retries)',        game_2),
    '3': ('Flashcards  (reveal answer if wrong)',   game_3),
    '4': ('Quiz        (multiple choice)',          game_4),
}


def main():
    problems = generate_problems()

    print(bold(cyan("\n========================================")))
    print(bold(cyan("  Math Facts: Addition & Subtraction ≤20")))
    print(bold(cyan("========================================")))

    while True:
        print(f"\n{bold('Select a game:')}")
        for key, (label, _) in GAMES.items():
            print(f"  {key}  {label}")
        print("  q  Quit\n")

        try:
            choice = input("Game: ").strip().lower()
        except (EOFError, KeyboardInterrupt):
            print("\nGoodbye!")
            break

        if choice == 'q':
            print("Goodbye!")
            break
        elif choice in GAMES:
            deck = list(problems)
            random.shuffle(deck)
            GAMES[choice][1](deck)
        else:
            print(red("  Invalid choice — enter 1, 2, 3, 4, or q."))


if __name__ == '__main__':
    main()
