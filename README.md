# Mini Tools Collection

A set of tiny, dependency-free tools — Python CLIs and self-contained static web apps (single HTML file each, save to your browser, deploy to Vercel with no config).

| Tool | CLI | Web app |
| --- | --- | --- |
| Expense tracker | `expense.py` | `index.html` (the site's landing page) |
| Task manager | `task.py` | `tasks.html` |
| Hospital ED ops dashboard | — | `dashboard.html` |
| Patient triage & vitals monitoring | — | `triage.html` |
| Medicine reminder | — | `medicine.html` |
| Women's outfit design recommender (Hindi) | — | `tailor.html` |
| Symptom advisor (causes / care / prevention) | — | `symptom.html` |

## Hospital ED Monitoring Dashboard

`dashboard.html` is a real-time **Emergency Department** operations monitor driven by a self-contained simulation (no backend, no real patient data). It shows:

- **KPI tiles** — patients in ED, waiting-to-be-seen + average wait, available ED beds, ambulances inbound
- **Active alerts** — live code alerts (Code Blue, Trauma Activation, Code Stroke, STEMI, Sepsis, etc.)
- **Triage breakdown** — current patients by ESI level (1 Resuscitation → 5 Non-urgent)
- **Unit capacity** — ED / ICU / Med-Surg / Pediatric occupancy, colored by utilization
- **Patient queue** and **incoming ambulances** with live ETA countdowns

Data updates every few seconds; acuity/severity use a fixed status palette (green→yellow→orange→red) with labels. Dark by default with a light toggle, and a Pause button to freeze the feed. **Simulated data for demonstration only — not connected to any real hospital or patient records.** Point it at a real EHR/monitoring API by replacing the simulation with `fetch` calls.

## Patient Triage & Vitals Monitoring

`triage.html` is a patient-level view (linked from the ops dashboard): a grid of live **monitor cards**, one per patient. Each shows ESI acuity, chief complaint, time in department, and continuously updating **vital signs** — HR, SpO₂, RR, BP, Temp — with an HR trend sparkline.

- Vitals are color-coded against simplified adult reference ranges: normal / **ABNORMAL** / **CRITICAL** (with text flags, never color alone).
- A patient with any critical vital **alarms** (pulsing red card + banner listing the breached vitals) and sorts to the top.
- Filter by ESI level, `＋ Triage arrival` to admit a patient, Pause to freeze. Thresholds are simplified for demo — **not real patients, not for clinical use.**

> On this machine Python is run with `py` (not `python`). Examples below use `py`.
> Open either `.html` file directly in a browser, or serve the folder with `py -m http.server 8000`.

---

# Task Manager

Command-line task manager. Tasks are stored in `tasks.json`.

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

### Options

- `-p, --priority` — `low`, `medium` (default), or `high`
- `-d, --due` — due date as `YYYY-MM-DD` (use `-d none` with `edit` to clear)

### Notes

- Tasks list sorted by: open first, then priority (high → low), then due date.
- Priority markers in the list: `!!` = high, `!` = medium.
- **Overdue** tasks (past their due date, not yet done) show `(OVERDUE <date>)`.
- Run `py task.py -h` or `py task.py <command> -h` for built-in help.

---

# Expense Tracker

Command-line expense tracker. Expenses are stored in `expenses.json`.

## Commands

| Command | Description |
| --- | --- |
| `py expense.py add 12.50 groceries` | Add an expense (amount + category) |
| `py expense.py add 40 transport -n "train pass" -d 2026-07-10` | With note + date |
| `py expense.py list` | List all expenses with a total |
| `py expense.py list --month 2026-07` | List expenses for a month |
| `py expense.py list --category groceries` | List expenses in a category |
| `py expense.py summary` | Spending by category, with % bars |
| `py expense.py summary --month 2026-07` | Category summary for a month |
| `py expense.py remove <id>` | Delete an expense |
| `py expense.py clear --yes` | Delete all expenses |

### Options

- `-n, --note` — optional note
- `-d, --date` — date as `YYYY-MM-DD` (defaults to today)
- `-m, --month` — filter by month `YYYY-MM` (on `list` / `summary`)
- `-c, --category` — filter by category (on `list` / `summary`)

### Notes

- Amounts are shown in Indian Rupees (₹) with Indian digit grouping (e.g. `₹1,50,000.00`). Change the `CURRENCY` constant near the top of `expense.py` (and `expenses.html`) to use another currency.
- Amounts must be greater than 0.
- The web app (`index.html`) adds a live category breakdown chart and a month picker.
