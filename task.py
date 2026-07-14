#!/usr/bin/env python3
"""A simple command-line task manager.

Tasks are stored as JSON in tasks.json next to this script.

Usage examples:
    python task.py add "Buy groceries"
    python task.py add "Finish report" --priority high --due 2026-07-20
    python task.py list
    python task.py list --all
    python task.py done 3
    python task.py undone 3
    python task.py remove 3
    python task.py clear
"""
import argparse
import json
import os
import sys
from datetime import datetime

DATA_FILE = os.path.join(os.path.dirname(os.path.abspath(__file__)), "tasks.json")

PRIORITIES = ("low", "medium", "high")
PRIORITY_RANK = {"high": 0, "medium": 1, "low": 2}


def load_tasks():
    if not os.path.exists(DATA_FILE):
        return []
    try:
        with open(DATA_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    except (json.JSONDecodeError, OSError) as e:
        print(f"Error reading {DATA_FILE}: {e}", file=sys.stderr)
        sys.exit(1)


def save_tasks(tasks):
    try:
        with open(DATA_FILE, "w", encoding="utf-8") as f:
            json.dump(tasks, f, indent=2)
    except OSError as e:
        print(f"Error writing {DATA_FILE}: {e}", file=sys.stderr)
        sys.exit(1)


def next_id(tasks):
    return max((t["id"] for t in tasks), default=0) + 1


def find_task(tasks, task_id):
    for t in tasks:
        if t["id"] == task_id:
            return t
    return None


def valid_date(value):
    try:
        datetime.strptime(value, "%Y-%m-%d")
        return value
    except ValueError:
        raise argparse.ArgumentTypeError(f"'{value}' is not a valid date (use YYYY-MM-DD)")


def cmd_add(args):
    tasks = load_tasks()
    task = {
        "id": next_id(tasks),
        "text": args.text,
        "done": False,
        "priority": args.priority,
        "due": args.due,
        "created": datetime.now().strftime("%Y-%m-%d %H:%M"),
    }
    tasks.append(task)
    save_tasks(tasks)
    print(f"Added task #{task['id']}: {task['text']}")


def is_overdue(task):
    if task["done"] or not task.get("due"):
        return False
    return task["due"] < datetime.now().strftime("%Y-%m-%d")


def render_tasks(tasks):
    tasks = sorted(tasks, key=lambda t: (t["done"], PRIORITY_RANK.get(t["priority"], 1), t["due"] or "9999-99-99"))
    for t in tasks:
        box = "[x]" if t["done"] else "[ ]"
        mark = {"high": "!!", "medium": "!", "low": " "}.get(t["priority"], " ")
        if t.get("due"):
            due = f" (OVERDUE {t['due']})" if is_overdue(t) else f" (due {t['due']})"
        else:
            due = ""
        print(f"{box} #{t['id']:<3} {mark:<2} {t['text']}{due}")


def cmd_list(args):
    tasks = load_tasks()
    if not args.all:
        tasks = [t for t in tasks if not t["done"]]
    if not tasks:
        print("No tasks. Add one with:  python task.py add \"Your task\"")
        return
    render_tasks(tasks)


def _set_done(args, value):
    tasks = load_tasks()
    task = find_task(tasks, args.id)
    if task is None:
        print(f"No task with id #{args.id}", file=sys.stderr)
        sys.exit(1)
    task["done"] = value
    save_tasks(tasks)
    state = "done" if value else "not done"
    print(f"Marked task #{args.id} as {state}: {task['text']}")


def cmd_done(args):
    _set_done(args, True)


def cmd_undone(args):
    _set_done(args, False)


def cmd_remove(args):
    tasks = load_tasks()
    task = find_task(tasks, args.id)
    if task is None:
        print(f"No task with id #{args.id}", file=sys.stderr)
        sys.exit(1)
    tasks = [t for t in tasks if t["id"] != args.id]
    save_tasks(tasks)
    print(f"Removed task #{args.id}: {task['text']}")


def cmd_clear(args):
    tasks = load_tasks()
    remaining = [t for t in tasks if not t["done"]]
    removed = len(tasks) - len(remaining)
    save_tasks(remaining)
    print(f"Cleared {removed} completed task(s).")


def cmd_edit(args):
    tasks = load_tasks()
    task = find_task(tasks, args.id)
    if task is None:
        print(f"No task with id #{args.id}", file=sys.stderr)
        sys.exit(1)
    if args.text is None and args.priority is None and args.due is None:
        print("Nothing to change. Provide new text and/or --priority/--due.", file=sys.stderr)
        sys.exit(1)
    if args.text is not None:
        task["text"] = args.text
    if args.priority is not None:
        task["priority"] = args.priority
    if args.due is not None:
        # Clear the due date with --due none (empty string is unreliable in some shells)
        task["due"] = None if args.due.lower() in ("", "none") else valid_date(args.due)
    save_tasks(tasks)
    print(f"Updated task #{args.id}: {task['text']}")


def cmd_find(args):
    tasks = load_tasks()
    keyword = args.keyword.lower()
    matches = [t for t in tasks if keyword in t["text"].lower()]
    if not args.all:
        matches = [t for t in matches if not t["done"]]
    if not matches:
        print(f"No tasks matching '{args.keyword}'.")
        return
    render_tasks(matches)


def build_parser():
    parser = argparse.ArgumentParser(description="A simple command-line task manager.")
    sub = parser.add_subparsers(dest="command", required=True)

    p_add = sub.add_parser("add", help="Add a new task")
    p_add.add_argument("text", help="The task description")
    p_add.add_argument("-p", "--priority", choices=PRIORITIES, default="medium",
                       help="Task priority (default: medium)")
    p_add.add_argument("-d", "--due", type=valid_date, help="Due date (YYYY-MM-DD)")
    p_add.set_defaults(func=cmd_add)

    p_list = sub.add_parser("list", help="List tasks")
    p_list.add_argument("-a", "--all", action="store_true", help="Include completed tasks")
    p_list.set_defaults(func=cmd_list)

    p_done = sub.add_parser("done", help="Mark a task as done")
    p_done.add_argument("id", type=int, help="Task id")
    p_done.set_defaults(func=cmd_done)

    p_undone = sub.add_parser("undone", help="Mark a task as not done")
    p_undone.add_argument("id", type=int, help="Task id")
    p_undone.set_defaults(func=cmd_undone)

    p_remove = sub.add_parser("remove", help="Remove a task")
    p_remove.add_argument("id", type=int, help="Task id")
    p_remove.set_defaults(func=cmd_remove)

    p_clear = sub.add_parser("clear", help="Remove all completed tasks")
    p_clear.set_defaults(func=cmd_clear)

    p_edit = sub.add_parser("edit", help="Edit a task's text, priority, or due date")
    p_edit.add_argument("id", type=int, help="Task id")
    p_edit.add_argument("text", nargs="?", help="New task description (optional)")
    p_edit.add_argument("-p", "--priority", choices=PRIORITIES, help="New priority")
    p_edit.add_argument("-d", "--due", help="New due date (YYYY-MM-DD), or 'none' to clear")
    p_edit.set_defaults(func=cmd_edit)

    p_find = sub.add_parser("find", help="Search tasks by keyword")
    p_find.add_argument("keyword", help="Text to search for (case-insensitive)")
    p_find.add_argument("-a", "--all", action="store_true", help="Include completed tasks")
    p_find.set_defaults(func=cmd_find)

    return parser


def main(argv=None):
    parser = build_parser()
    args = parser.parse_args(argv)
    args.func(args)


if __name__ == "__main__":
    main()
