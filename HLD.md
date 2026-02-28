# High-Level Design Document
## Church Community Population Tracker
**Version:** 1.1
**Date:** 2026-02-28
**Status:** Current

---

## Change Log

| Version | Date | Changes |
|---|---|---|
| 1.0 | 2026-02-28 | Initial release |
| 1.1 | 2026-02-28 | Added Date of Death column to residents table; added Ukrainian language support (`lang.py`); added cross-platform install scripts |

---

## 1. Purpose and Scope

The Church Community Population Tracker is a standalone desktop application that allows a church
administrator to maintain a register of community members grouped by their home address. It tracks
personal milestones (birth, baptism, marriage, death), provides a chronological event history per
household, and can export the full register to CSV or Excel for external reporting.

The UI and all exported data can be displayed in **English or Ukrainian**, switchable at any time
from the Settings menu.

**In scope:**
- Managing household addresses within a single city
- Managing individual residents per address
- Recording and displaying life events per resident
- Exporting data to CSV and Excel formats
- English / Ukrainian UI language selection

**Out of scope:**
- Network access or cloud synchronisation
- Multi-user / multi-site operation
- Financial records, attendance, or ministry assignments

---

## 2. System Context

```
┌──────────────────────────────────────────────────────────────────┐
│                        End User (PC)                             │
│                                                                  │
│   ┌─────────────────────────────────────────────────────────┐    │
│   │           Church Community Tracker (Python)             │    │
│   │                                                         │    │
│   │    Presentation Layer  ──►  Business Logic  ──►  DB     │    │
│   │    (tkinter / ttk)          (database.py)    (SQLite)   │    │
│   │              │                                          │    │
│   │         lang.py  (i18n — all UI strings EN/UK)          │    │
│   └─────────────────────────────────────────────────────────┘    │
│                              │                                   │
│                    ┌─────────▼──────────┐                        │
│                    │  church.db (file)  │                        │
│                    └────────────────────┘                        │
│                                                                  │
│              Export: residents.csv / residents.xlsx              │
└──────────────────────────────────────────────────────────────────┘
```

The application runs entirely on the user's local machine. There are no external services,
no network connections, and no authentication layer. All data lives in a single SQLite file
(`church.db`) stored next to the application executable.

---

## 3. Architecture Overview

The application follows a classic **three-layer architecture** with a cross-cutting
internationalisation (i18n) module:

```
┌─────────────────────────────────────────────────────────────────┐
│  PRESENTATION LAYER (ui/)                                       │
│  main.py · address_list.py · resident_view.py · dialogs.py      │
│  Renders UI, handles user input, delegates to database layer    │
├─────────────────────────────────────────────────────────────────┤
│  DATA / BUSINESS LOGIC LAYER                                    │
│  database.py · export.py                                        │
│  All SQL queries, CRUD, event logging, export formatting        │
├─────────────────────────────────────────────────────────────────┤
│  DOMAIN MODEL LAYER                                             │
│  models.py                                                      │
│  Pure Python dataclasses: Address, Resident, Event              │
├─────────────────────────────────────────────────────────────────┤
│  PERSISTENCE LAYER                                              │
│  SQLite via Python built-in sqlite3 — church.db                 │
└─────────────────────────────────────────────────────────────────┘

  ┌──────────────────────────────────────────────────────────────┐
  │  CROSS-CUTTING: lang.py (i18n)                               │
  │  Used by all layers above — provides translated strings      │
  │  for any registered key in English or Ukrainian              │
  └──────────────────────────────────────────────────────────────┘
```

The UI layer never constructs SQL — it only calls functions from `database.py` and works
with model objects. The database layer never imports anything from the `ui/` package,
keeping a clean separation of concerns.

---

## 4. Project File Structure

```
church_tracker/
├── main.py              Entry point, MainWindow, menu bar
├── models.py            Dataclasses: Address, Resident, Event
├── database.py          SQLite CRUD + seed data
├── export.py            CSV and Excel export
├── lang.py              i18n — all UI strings in EN and UK
├── install.py           Cross-platform installer (called by scripts below)
├── install.sh           Linux / macOS installer (bash install.sh)
├── install.bat          Windows installer    (double-click)
├── requirements.txt     openpyxl
├── pyrightconfig.json   Pylance / Pyright IDE config
├── church.db            SQLite database (created on first run)
└── ui/
    ├── __init__.py
    ├── address_list.py  Left panel — address list
    ├── resident_view.py Right panel — residents table + event log
    └── dialogs.py       All modal dialogs
```

---

## 5. Module Descriptions

### 5.1 `main.py` — Application Entry Point

| Responsibility | Detail |
|---|---|
| Bootstrap | Calls `db.init_db()`, `db.seed_dummy_data()`, loads saved language via `lang.set_lang()` |
| First-run | Prompts for city name if not yet configured |
| Main window | `MainWindow(tk.Tk)` — top-level window, 1050×660 px |
| Menu bar | File (Export CSV/Excel, Exit), Settings (City Name, Language), Help (About) |
| Layout | Horizontal `PanedWindow` split: left panel (240 px) + right panel (fills) |
| Status bar | Single-line label at bottom reflecting current selection or action |
| Event routing | `_on_address_selected()` bridges the two panels |

### 5.2 `models.py` — Domain Model

Three `@dataclass` classes carry data between layers:

| Class | Key Fields | Notes |
|---|---|---|
| `Address` | `id`, `street`, `notes`, `active_count` | `active_count` is computed by a SQL aggregate, not stored |
| `Resident` | `id`, `address_id`, `first/last_name`, `birth/baptism/marriage/death_date`, `status`, `notes` | `status` ∈ `{'active', 'deceased'}` |
| `Event` | `id`, `resident_id`, `event_type`, `event_date`, `description`, `created_at`, `resident_name` | `resident_name` is populated by JOIN, not stored |

Computed properties on `Resident`:
- `full_name` → `"{first_name} {last_name}"`
- `is_baptized` → `baptism_date is not None`
- `is_married` → `marriage_date is not None`

### 5.3 `database.py` — Data Access Layer

Provides all database operations grouped by entity:

| Group | Functions |
|---|---|
| Lifecycle | `init_db()`, `seed_dummy_data()` |
| Config | `get_config(key)`, `set_config(key, value)` |
| Addresses | `get_addresses()`, `add_address()`, `update_address()`, `delete_address()` |
| Residents | `get_residents(addr_id)`, `get_all_residents()`, `add_resident()`, `update_resident()`, `delete_resident()`, `mark_deceased()` |
| Events | `get_events_for_address(addr_id)`, `add_event()` |

All functions open a fresh connection via `get_connection()`, use it as a context manager
(auto-commit / auto-close), and convert raw `sqlite3.Row` results into model objects via
`_row_to_resident()` and `_row_to_event()` helpers.

`PRAGMA foreign_keys = ON` is enabled on every connection so cascading deletes work correctly.

The `config` table stores two runtime keys: `city` (city name) and `language` (`en` or `uk`).

### 5.4 `export.py` — Export Module

| Function | Output | Library |
|---|---|---|
| `export_csv(path, residents)` | UTF-8 CSV with header row | `csv` (built-in) |
| `export_excel(path, residents)` | `.xlsx` with styled header row and auto-sized columns | `openpyxl` (third-party) |

Both functions sort residents alphabetically by last name then first name. Column headers
and status values (`active` / `deceased`) are rendered in the **currently active language**
via `lang.get()`. The address name is resolved from a module-level `_ADDRESS_CACHE` dict
populated lazily on first call.

### 5.5 `lang.py` — Internationalisation (i18n)

Central repository for all user-visible strings. Supports **English** (`en`) and
**Ukrainian** (`uk`).

| Item | Detail |
|---|---|
| Storage | `_STRINGS` dict — `key → {lang_code → translated_string}` |
| Supported languages | `SUPPORTED = {"en": "English", "uk": "Українська"}` |
| Active language | Module-level `_current` variable; set at startup from DB config |
| Main API | `lang.get(key, **kwargs)` — returns translated string, with optional `.format()` substitutions |
| Event helpers | `lang.event_types()` — localized list for Combobox; `lang.event_type_to_key()` — converts localized label back to DB key; `lang.event_key_to_label()` — converts DB key to localized label |
| Language switch | `lang.set_lang(code)` — changes `_current`; new value saved to DB config; takes effect on next app restart |

Event types are **always stored in English** in the database (`birth`, `baptism`, `marriage`,
`death`), ensuring data integrity regardless of which language was active when the event
was recorded. They are translated to the current language only at display time.

### 5.6 `ui/address_list.py` — Left Panel

`AddressListPanel(ttk.Frame)` manages the address list:

- `tk.Listbox` with vertical scrollbar, displays `"  {street}  ({active_count})"`
- Add / Edit / Delete buttons (labels from `lang.get()`)
- Double-click on an address opens the Edit dialog
- Selection change fires the `on_select` callback (injected from `MainWindow`) to update the right panel
- `refresh()` re-queries the database and restores the previously selected address by ID

### 5.7 `ui/resident_view.py` — Right Panel

`ResidentViewPanel(ttk.Frame)` is divided into two vertical sections:

**Top section — Residents table (`ttk.Treeview`)**

| Column | Content |
|---|---|
| Name | `full_name` |
| Date of Birth | `birth_date` (YYYY-MM-DD) |
| Baptized | `yes` / `no` (localized) |
| Married | `yes` / `no` (localized) |
| Status | `active` / `deceased` (localized; deceased rows rendered in gray) |
| Date of Death | `death_date` (YYYY-MM-DD); blank for active residents |

Action buttons: **+ Add Member**, **Edit**, **Record Event**, **Mark Deceased**, **Remove**
(all labels from `lang.get()`)

**Bottom section — Event History (`tk.Text`, read-only)**

Chronological log of all events for all residents at the selected address, newest first.
Each line: `{date}  {icon} {EVENT_TYPE}  {resident_name} — {description}`

Event icons: `★` birth, `✝` baptism, `♥` marriage, `✟` death

Event type labels in the log are rendered in the current language.

### 5.8 `ui/dialogs.py` — Modal Dialogs

All dialogs are `tk.Toplevel` with `grab_set()` (modal) and `transient(parent)`.
They store the result in `self.result` and destroy themselves; the caller inspects
`dlg.result` after `wait_window()` returns.

| Dialog | Purpose | Result type |
|---|---|---|
| `CityDialog` | Set / change city name | `str` |
| `AddressDialog` | Add or edit an address | `Address` |
| `ResidentDialog` | Add or edit a resident (all date fields) | `Resident` |
| `MarkDeceasedDialog` | Quick death-date entry | `str` (date) |
| `EventDialog` | Record any life event with type, date, description | `Event` |
| `LanguageDialog` | Select UI language (radio buttons) | `str` (lang code) |

All date fields use the shared `_date_entry(parent, label_key, row)` helper which creates
a labeled `ttk.Entry` bound to a `StringVar`, a clear (✕) button, and a format hint label.
The `label_key` is a `lang` key, so the label is automatically translated. Date format is
validated against `^\d{4}-\d{2}-\d{2}$` via `_validate_date()` before saving.

### 5.9 `install.py` — Cross-Platform Installer

Standalone Python script that runs the full installation sequence:

1. Checks Python version ≥ 3.8
2. Checks that `tkinter` is importable — prints OS-specific install instructions if missing
3. Runs `pip install openpyxl`
4. Calls `db.init_db()` and `db.seed_dummy_data()` to create and populate `church.db`
5. Creates a platform-appropriate launch shortcut (`run.sh` on Linux/macOS, `run.bat` on Windows)

---

## 6. Database Schema

```
┌────────────────────────────────────────────────┐
│  config                                        │
│  ────────────────────────────────────────────  │
│  key   TEXT  PK                                │
│  value TEXT                                    │
│                                                │
│  Known keys:                                   │
│    city     — city name string                 │
│    language — 'en' or 'uk'                     │
└────────────────────────────────────────────────┘

┌────────────────────────────────────────────────┐
│  addresses                                     │
│  ────────────────────────────────────────────  │
│  id      INTEGER  PK AUTOINCREMENT             │
│  street  TEXT     NOT NULL                     │
│  notes   TEXT     DEFAULT ''                   │
└───────────────────────┬────────────────────────┘
                        │ 1
                        │
                        │ N
┌───────────────────────▼────────────────────────┐
│  residents                                     │
│  ────────────────────────────────────────────  │
│  id             INTEGER  PK AUTOINCREMENT      │
│  address_id     INTEGER  FK → addresses(id)    │
│                          ON DELETE CASCADE     │
│  first_name     TEXT     NOT NULL              │
│  last_name      TEXT     NOT NULL              │
│  birth_date     TEXT     (YYYY-MM-DD | NULL)   │
│  baptism_date   TEXT     (YYYY-MM-DD | NULL)   │
│  marriage_date  TEXT     (YYYY-MM-DD | NULL)   │
│  death_date     TEXT     (YYYY-MM-DD | NULL)   │
│  status         TEXT     DEFAULT 'active'      │
│  notes          TEXT     DEFAULT ''            │
└───────────────────────┬────────────────────────┘
                        │ 1
                        │
                        │ N
┌───────────────────────▼────────────────────────┐
│  events                                        │
│  ────────────────────────────────────────────  │
│  id           INTEGER  PK AUTOINCREMENT        │
│  resident_id  INTEGER  FK → residents(id)      │
│                        ON DELETE CASCADE       │
│  event_type   TEXT     NOT NULL                │
│               ('birth'|'baptism'|              │
│                'marriage'|'death')             │
│  event_date   TEXT     NOT NULL (YYYY-MM-DD)   │
│  description  TEXT     DEFAULT ''              │
│  created_at   TEXT     DEFAULT datetime('now') │
└────────────────────────────────────────────────┘
```

**Cascade behaviour:**
- Deleting an `address` cascades to delete all its `residents`
- Deleting a `resident` cascades to delete all their `events`

**Dates** are stored as plain `TEXT` in ISO-8601 format (`YYYY-MM-DD`). SQLite's
lexicographic ordering on text correctly sorts ISO dates, so `ORDER BY event_date DESC`
works as expected.

**Event types** are always stored in English regardless of the active UI language.

---

## 7. Key Data Flows

### 7.1 Startup

```
main.py: MainWindow.__init__()
  │
  ├── db.init_db()                    → CREATE TABLE IF NOT EXISTS (idempotent)
  ├── db.seed_dummy_data()            → INSERT sample data only if DB is empty
  ├── db.get_config('language')
  │     └── lang.set_lang(code)       → set active language before any UI is built
  ├── db.get_config('city')
  │     └── if empty → CityDialog → db.set_config('city', ...)
  ├── MainWindow._build_menu()        → all labels via lang.get()
  └── MainWindow._build_ui()
        ├── AddressListPanel(on_select=_on_address_selected)
        │     └── self.refresh() → db.get_addresses() → populate Listbox
        └── ResidentViewPanel → _show_placeholder()
```

### 7.2 Selecting an Address

```
User clicks address in Listbox
  │
  └── AddressListPanel._on_listbox_select()
        └── self._on_select(address)           [callback to MainWindow]
              └── MainWindow._on_address_selected(address)
                    ├── ResidentViewPanel.load_address(address)
                    │     ├── db.get_residents(address.id)   → populate Treeview
                    │     └── db.get_events_for_address(id)  → populate Event log
                    └── status bar update (via lang.get('status_viewing', ...))
```

### 7.3 Adding a New Resident

```
User clicks "+ Add Member"
  │
  └── ResidentViewPanel._add_resident()
        ├── ResidentDialog(parent, address_id)    [modal — all labels localized]
        │     └── dlg.result = Resident(...)
        ├── db.add_resident(dlg.result)           → INSERT residents
        ├── if birth_date: db.add_event(birth)    → INSERT events (description via lang.get())
        ├── if death_date: db.add_event(death)    → INSERT events
        ├── _refresh_residents()                  → re-query + repopulate Treeview
        └── _refresh_events()                     → re-query + repopulate log
```

### 7.4 Marking a Resident as Deceased

```
User selects resident, clicks "Mark Deceased"
  │
  └── ResidentViewPanel._mark_deceased()
        ├── guard: already deceased? → showinfo, return
        ├── MarkDeceasedDialog(parent, resident)  [modal]
        │     └── dlg.result = "YYYY-MM-DD"
        ├── db.mark_deceased(res.id, date)        → UPDATE residents SET status='deceased', death_date=?
        ├── db.add_event(death_event)             → INSERT events
        ├── _refresh_residents()
        └── _refresh_events()
```

### 7.5 Exporting to Excel

```
User: File → Export to Excel…
  │
  └── MainWindow._export_excel()
        ├── filedialog.asksaveasfilename()
        ├── db.get_all_residents()
        └── export.export_excel(path, residents)
              ├── import openpyxl  (raises RuntimeError if missing)
              ├── _headers() → column names via lang.get() in current language
              ├── create Workbook, style header row
              ├── write one row per resident (sorted by last, first name)
              │     └── status values also via lang.get()
              ├── auto-size columns
              └── wb.save(path)
```

### 7.6 Changing Language

```
User: Settings → Language / Мова…
  │
  └── MainWindow._change_language()
        ├── LanguageDialog(parent, current_lang)  [modal — radio buttons EN / UK]
        │     └── dlg.result = 'en' | 'uk'
        ├── db.set_config('language', dlg.result) → saved to DB
        └── messagebox.showinfo(lang_restart_note)
              └── User restarts app → startup reads new language → full UI rebuilt
```

---

## 8. UI Layout

```
┌──────────────────────────────────────────────────────────────────────────────────────┐
│  File   Settings   Help                              [menu bar]                      │
├──────────────────┬───────────────────────────────────────────────────────────────────┤
│  ADDRESSES       │  56 Maple Street                [right header]                    │
│  ──────────────  │  ───────────────────────────────────────────────────────────────  │
│  12 Church Ln(3) │  Name         DOB        Baptized Married Status   Date of Death  │
│  34 Oak Ave  (2) │  Maria Novak  1948-09-14  yes      yes    active                  │
│  56 Maple St (2) │  Peter Novak  1945-06-07  yes      yes    deceased 2021-11-30     │
│  78 Cedar Rd (3) │  Thomas Novak 1970-03-25  yes      yes    active                  │
│                  │                                                                   │
│                  │  [+Add Member] [Edit] [Record Event] [Mark Deceased] [Remove]     │
│  [+Add][Edit]    │  ───────────────────────────────────────────────────────────────  │
│  [Delete]        │  Event History                                                    │
│                  │  2021-11-30  ✟ DEATH       Peter Novak passed away                │
│                  │  1968-04-27  ♥ MARRIAGE    Peter Novak married ...                │
│                  │  1948-09-14  ★ BIRTH       Peter Novak was born                   │
├──────────────────┴───────────────────────────────────────────────────────────────────┤
│  Viewing: 56 Maple Street  •  2 active resident(s)   [status bar]                    │
└──────────────────────────────────────────────────────────────────────────────────────┘
```

The horizontal split is a `ttk.PanedWindow` — the user can drag the divider.
Initial left panel width is 240 px; the right panel takes the remaining space.

All visible text (column headers, button labels, menu items, dialog labels, messages)
is rendered in the currently selected language.

---

## 9. Technology Decisions

| Decision | Choice | Rationale |
|---|---|---|
| Language | Python 3.8+ | Cross-platform, pre-installed on macOS/Linux; simple Windows installer |
| GUI toolkit | `tkinter` + `ttk` | Built into Python standard library — zero extra install for the UI |
| Database | SQLite via `sqlite3` | Built into Python; single-file, zero-configuration, sufficient for community scale |
| Excel export | `openpyxl` | De-facto standard Python library for `.xlsx`; the only external dependency |
| i18n approach | Custom `lang.py` dict | No external library needed; simple key→dict lookup; trivially extensible to more languages |
| Event types in DB | English keys only | Switching UI language never corrupts stored data |
| Packaging (Windows) | PyInstaller `--onefile --windowed` | Produces a single portable `.exe` with no Python install required |
| Date format | ISO-8601 text `YYYY-MM-DD` | Human-readable, sortable lexicographically, universally understood |
| Modal dialogs | `tk.Toplevel` with `grab_set()` | Keeps all dialogs in the same process/window; `wait_window()` provides synchronous UX |

---

## 10. Constraints and Known Limitations

| Limitation | Detail |
|---|---|
| Single city | The app tracks one city, stored as a single config key. Multi-city use would require a schema change. |
| Language restart required | Language change takes effect only after restarting the app; the running UI is not rebuilt live. |
| No user authentication | Data is not protected — anyone with access to the PC can open the app or the `.db` file. |
| No backup / sync | No automatic backup. Users should manually copy `church.db` regularly. |
| No marriage linking | Marriage date is stored per individual, not as a relation between two residents. |
| Date validation | Validates format (`YYYY-MM-DD`) but does not check calendar validity (e.g. `2024-02-30`). |
| Single-file export | Export always exports all residents; no per-address or filtered export. |
| No search | No full-text search across residents or events. |
| No undo | All changes are immediately committed to the database. |

---

## 11. Deployment

### First-time installation

| Platform | Command |
|---|---|
| Windows | Double-click `install.bat` |
| Linux | `bash install.sh` |
| macOS | `bash install.sh` |

The installer checks Python ≥ 3.8, verifies `tkinter` is present (with OS-specific fix
instructions if not), installs `openpyxl`, initialises the database with sample data,
and creates a launch shortcut (`run.sh` or `run.bat`).

### Launching the app after installation

| Platform | Command |
|---|---|
| Windows | Double-click `run.bat` or `python main.py` |
| Linux / macOS | `bash run.sh` or `python3 main.py` |

### Building a Windows standalone executable

```bash
pip install pyinstaller
pyinstaller --onefile --windowed --name "ChurchTracker" main.py
# Output: dist/ChurchTracker.exe
```

The resulting `.exe` bundles Python and all modules. Copy `ChurchTracker.exe`
to any Windows PC — no installation needed. `church.db` will be created in the
same directory as the `.exe` on first launch.

### Data file location

| Platform | `church.db` path |
|---|---|
| Source run | Same directory as `main.py` |
| PyInstaller `.exe` | Same directory as the `.exe` |

---

## 12. Future Extension Points

| Feature | Suggested Approach |
|---|---|
| Additional languages | Add a new `{"lang_code": "translation"}` entry to each key in `lang._STRINGS`; add the code to `lang.SUPPORTED` |
| Live language switch | Rebuild all UI widgets after `lang.set_lang()` instead of requiring restart |
| Search / filter residents | Add a search bar above the address list or treeview; filter in-memory or via SQL `LIKE` |
| Per-address export | Pass `address_id` filter to export functions |
| Print / PDF report | Use `reportlab` or export to HTML and open in browser |
| Backup / restore | Add "File → Backup…" that copies `church.db` to a chosen path |
| Marriage links | Add a `marriages` table with `(resident_id_a, resident_id_b, date)` |
| Multiple cities | Add a `cities` table; link `addresses` to a city |
| Dark mode | `ttk` themes can be swapped via `ttk.Style().theme_use('...')` |
| Import from CSV | Reverse of the export path; validate and `INSERT` rows from a spreadsheet |
