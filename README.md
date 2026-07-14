# Task Manager (CLI)

A tiny, dependency-free command-line task manager. Tasks are stored in `tasks.json`.

> On this machine Python is run with `py` (not `python`). Examples below use `py`.

## Commands

| Command | Description |
| --- | --- |
| `py task.py add "text"` | Add a task |
| `py task.py add "text" -p high -d 2026-07-20` | Add with priority + due date |
| `py task.py list` | List open tasks |
| `py task.py list --all` | List all tasks, including completed |
| `py task.py done <id>` | Mark a task done |
| `py task.py undone <id>` | Mark a task not done |
| `py task.py remove <id>` | Delete a task |
| `py task.py clear` | Remove all completed tasks |
| `py task.py edit <id> "new text"` | Edit a task's text, priority, or due date |
| `py task.py find <keyword>` | Search tasks by keyword |

## Options

- `-p, --priority` — `low`, `medium` (default), or `high`
- `-d, --due` — due date as `YYYY-MM-DD`

### edit

Change any combination of text, priority, and due date. The text argument is optional.

```powershell
py task.py edit 3 "Renamed task"        # change text
py task.py edit 3 -p high               # change priority only
py task.py edit 3 -d 2026-08-01         # change due date only
py task.py edit 3 -d none               # clear the due date
```

### find

Case-insensitive keyword search. Add `--all` to include completed tasks.

```powershell
py task.py find groceries
py task.py find report --all
```

## Notes

- Tasks list sorted by: open first, then priority (high → low), then due date.
- Priority markers in the list: `!!` = high, `!` = medium.
- **Overdue** tasks (past their due date, not yet done) show `(OVERDUE <date>)` instead of `(due <date>)`.
- Run `py task.py -h` or `py task.py <command> -h` for built-in help.
