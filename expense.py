#!/usr/bin/env python3
"""A simple command-line expense tracker.

Expenses are stored as JSON in expenses.json next to this script.

Usage examples:
    python expense.py add 12.50 groceries
    python expense.py add 40 transport --note "train pass" --date 2026-07-10
    python expense.py list
    python expense.py list --month 2026-07
    python expense.py list --category groceries
    python expense.py summary
    python expense.py summary --month 2026-07
    python expense.py remove 3
    python expense.py clear
"""
import argparse
import json
import os
import sys
from datetime import datetime

# Ensure non-ASCII output (e.g. the rupee symbol) prints on Windows consoles,
# which otherwise default to a codec that can't encode it.
try:
    sys.stdout.reconfigure(encoding="utf-8")
    sys.stderr.reconfigure(encoding="utf-8")
except (AttributeError, ValueError):
    pass

DATA_FILE = os.path.join(os.path.dirname(os.path.abspath(__file__)), "expenses.json")

# Change this to your preferred currency symbol (e.g. "$", "EUR ").
CURRENCY = "₹"  # Indian Rupee (₹)


def load_expenses():
    if not os.path.exists(DATA_FILE):
        return []
    try:
        with open(DATA_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    except (json.JSONDecodeError, OSError) as e:
        print(f"Error reading {DATA_FILE}: {e}", file=sys.stderr)
        sys.exit(1)


def save_expenses(expenses):
    try:
        with open(DATA_FILE, "w", encoding="utf-8") as f:
            json.dump(expenses, f, indent=2)
    except OSError as e:
        print(f"Error writing {DATA_FILE}: {e}", file=sys.stderr)
        sys.exit(1)


def next_id(expenses):
    return max((e["id"] for e in expenses), default=0) + 1


def money(amount):
    """Format an amount with the currency symbol and Indian digit grouping."""
    sign = "-" if amount < 0 else ""
    whole, dec = f"{abs(amount):.2f}".split(".")
    if len(whole) > 3:
        head, last3 = whole[:-3], whole[-3:]
        groups = []
        while len(head) > 2:
            groups.insert(0, head[-2:])
            head = head[:-2]
        if head:
            groups.insert(0, head)
        whole = ",".join(groups) + "," + last3
    return f"{CURRENCY}{sign}{whole}.{dec}"


def positive_amount(value):
    try:
        amount = float(value)
    except ValueError:
        raise argparse.ArgumentTypeError(f"'{value}' is not a number")
    if amount <= 0:
        raise argparse.ArgumentTypeError("amount must be greater than 0")
    return round(amount, 2)


def valid_date(value):
    try:
        datetime.strptime(value, "%Y-%m-%d")
        return value
    except ValueError:
        raise argparse.ArgumentTypeError(f"'{value}' is not a valid date (use YYYY-MM-DD)")


def valid_month(value):
    try:
        datetime.strptime(value, "%Y-%m")
        return value
    except ValueError:
        raise argparse.ArgumentTypeError(f"'{value}' is not a valid month (use YYYY-MM)")


def cmd_add(args):
    expenses = load_expenses()
    expense = {
        "id": next_id(expenses),
        "amount": args.amount,
        "category": args.category.lower(),
        "note": args.note or "",
        "date": args.date or datetime.now().strftime("%Y-%m-%d"),
    }
    expenses.append(expense)
    save_expenses(expenses)
    print(f"Added #{expense['id']}: {money(expense['amount'])} on {expense['category']} ({expense['date']})")


def _filtered(expenses, args):
    result = expenses
    if getattr(args, "month", None):
        result = [e for e in result if e["date"].startswith(args.month)]
    if getattr(args, "category", None):
        cat = args.category.lower()
        result = [e for e in result if e["category"] == cat]
    return result


def cmd_list(args):
    expenses = _filtered(load_expenses(), args)
    if not expenses:
        print("No expenses. Add one with:  python expense.py add 9.99 category")
        return
    expenses.sort(key=lambda e: (e["date"], e["id"]))
    total = 0.0
    for e in expenses:
        note = f"  - {e['note']}" if e["note"] else ""
        print(f"#{e['id']:<3} {e['date']}  {money(e['amount']):>12}  {e['category']}{note}")
        total += e["amount"]
    print("-" * 44)
    print(f"{'TOTAL':<16}{money(total):>12}  ({len(expenses)} item(s))")


def cmd_summary(args):
    expenses = _filtered(load_expenses(), args)
    if not expenses:
        print("No expenses to summarize.")
        return
    totals = {}
    for e in expenses:
        totals[e["category"]] = totals.get(e["category"], 0.0) + e["amount"]
    grand = sum(totals.values())
    scope = f" for {args.month}" if getattr(args, "month", None) else ""
    print(f"Spending by category{scope}:")
    for cat, amt in sorted(totals.items(), key=lambda kv: kv[1], reverse=True):
        pct = (amt / grand * 100) if grand else 0
        bar = "#" * round(pct / 5)
        print(f"  {cat:<14} {money(amt):>12}  {pct:5.1f}%  {bar}")
    print("-" * 44)
    print(f"  {'TOTAL':<14} {money(grand):>12}")


def cmd_remove(args):
    expenses = load_expenses()
    match = next((e for e in expenses if e["id"] == args.id), None)
    if match is None:
        print(f"No expense with id #{args.id}", file=sys.stderr)
        sys.exit(1)
    expenses = [e for e in expenses if e["id"] != args.id]
    save_expenses(expenses)
    print(f"Removed #{args.id}: {money(match['amount'])} on {match['category']}")


def cmd_clear(args):
    expenses = load_expenses()
    if not args.yes:
        print(f"This will delete all {len(expenses)} expense(s). Re-run with --yes to confirm.")
        return
    save_expenses([])
    print(f"Cleared {len(expenses)} expense(s).")


def build_parser():
    parser = argparse.ArgumentParser(description="A simple command-line expense tracker.")
    sub = parser.add_subparsers(dest="command", required=True)

    p_add = sub.add_parser("add", help="Add an expense")
    p_add.add_argument("amount", type=positive_amount, help="Amount spent (e.g. 12.50)")
    p_add.add_argument("category", help="Category (e.g. groceries, transport)")
    p_add.add_argument("-n", "--note", help="Optional note")
    p_add.add_argument("-d", "--date", type=valid_date, help="Date (YYYY-MM-DD), defaults to today")
    p_add.set_defaults(func=cmd_add)

    p_list = sub.add_parser("list", help="List expenses")
    p_list.add_argument("-m", "--month", type=valid_month, help="Filter by month (YYYY-MM)")
    p_list.add_argument("-c", "--category", help="Filter by category")
    p_list.set_defaults(func=cmd_list)

    p_summary = sub.add_parser("summary", help="Show spending by category")
    p_summary.add_argument("-m", "--month", type=valid_month, help="Filter by month (YYYY-MM)")
    p_summary.add_argument("-c", "--category", help="Filter by category")
    p_summary.set_defaults(func=cmd_summary)

    p_remove = sub.add_parser("remove", help="Remove an expense")
    p_remove.add_argument("id", type=int, help="Expense id")
    p_remove.set_defaults(func=cmd_remove)

    p_clear = sub.add_parser("clear", help="Delete all expenses")
    p_clear.add_argument("--yes", action="store_true", help="Confirm deletion")
    p_clear.set_defaults(func=cmd_clear)

    return parser


def main(argv=None):
    parser = build_parser()
    args = parser.parse_args(argv)
    args.func(args)


if __name__ == "__main__":
    main()
