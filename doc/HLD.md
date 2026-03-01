# High-Level Design Document
## Church Community Population Tracker
**Version:** 1.5
**Date:** 2026-03-01
**Status:** Current

---

## Change Log

| Version | Date | Changes |
|---|---|---|
| 1.0 | 2026-02-28 | Initial release |
| 1.1 | 2026-02-28 | Added Date of Death column to residents table; added Ukrainian language support (`lang.py`); added cross-platform install scripts |
| 1.2 | 2026-02-28 | Added import from CSV/Excel; hardcoded city name (Kulykiv); DD.MM.YYYY display format for all dates; View (read-only) button; address format "Street Name Number" with Python-based Unicode sort; removed dummy seed data |
| 1.3 | 2026-02-28 | Added Father, Mother, Husband/Wife fields to Resident; DB migration for existing databases; active parishioner count in address panel |
| 1.4 | 2026-02-28 | Added "left" status (Mark Left / Виїхав); real-time search filter in both panels; window/taskbar icon (`img/church.png` + `church.ico`); fixed `install.py` crash; fixed export/import for "left" status |
| 1.5 | 2026-03-01 | CSV export defaults to `backup/` folder; Excel export defaults to `xlsx-reports/` folder; both folders created automatically on first export |

---

## 1. Purpose and Scope

The Church Community Population Tracker is a standalone desktop application that allows a church
administrator to maintain a register of community members grouped by their home address. It tracks
personal milestones (birth, baptism, marriage, death) and family relationships (father, mother,
spouse), provides a chronological event history per household, and can export the full register to
CSV or Excel for external reporting.

The UI and all exported data can be displayed in **English or Ukrainian**, switchable at any time
from the Settings menu.

**In scope:**
- Managing household addresses within a single city (Kulykiv / Куликів)
- Managing individual residents per address
- Recording and displaying life events per resident
- Exporting data to CSV and Excel formats
- Importing data from CSV and Excel files
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
│     Import / Export: residents.csv / residents.xlsx              │
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
│  All SQL queries, CRUD, event logging, export/import formatting │
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
├── database.py          SQLite CRUD + schema migration
├── export.py            CSV and Excel export and import
├── lang.py              i18n — all UI strings in EN and UK
├── install.py           Cross-platform installer (called by scripts below)
├── install.sh           Linux / macOS installer (bash install.sh)
├── install.bat          Windows installer    (double-click)
├── requirements.txt     openpyxl
├── pyrightconfig.json   Pylance / Pyright IDE config
├── church.db            SQLite database (created on first run)
├── backup/              Default destination for CSV exports (created on first export)
├── xlsx-reports/        Default destination for Excel exports (created on first export)
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
| Bootstrap | Calls `db.init_db()`, loads saved language via `lang.set_lang()` |
| Main window | `MainWindow(tk.Tk)` — top-level window, 1050×660 px |
| Title | Includes hardcoded city name from `lang.get('city_name')` — "Kulykiv" / "Куликів" |
| Menu bar | File (Export CSV/Excel, Import CSV/Excel, Exit), Settings (Language), Help (About) |
| Layout | Horizontal `tk.PanedWindow` split: left panel (270 px) + right panel (fills) |
| Status bar | Single-line label at bottom reflecting current selection or action |
| Event routing | `_on_address_selected()` bridges the two panels; `on_change` callback refreshes address list after resident mutations |

### 5.2 `models.py` — Domain Model

Three `@dataclass` classes carry data between layers:

| Class | Key Fields | Notes |
|---|---|---|
| `Address` | `id`, `street`, `notes`, `active_count` | `active_count` is computed by SQL aggregate, not stored |
| `Resident` | `id`, `address_id`, `first/last_name`, `father`, `mother`, `spouse`, `birth/baptism/marriage/death_date`, `status`, `notes` | `status` ∈ `{'active', 'deceased', 'left'}` |
| `Event` | `id`, `resident_id`, `event_type`, `event_date`, `description`, `created_at`, `resident_name` | `resident_name` is populated by JOIN, not stored |

Computed properties on `Resident`:
- `full_name` → `"{first_name} {last_name}"`
- `is_baptized` → `baptism_date is not None`
- `is_married` → `marriage_date is not None or bool(spouse)`

### 5.3 `database.py` — Data Access Layer

Provides all database operations grouped by entity:

| Group | Functions |
|---|---|
| Lifecycle | `init_db()` — creates tables + runs column migrations |
| Config | `get_config(key)`, `set_config(key, value)` |
| Addresses | `get_addresses()`, `add_address()`, `update_address()`, `delete_address()`, `find_or_create_address()` |
| Residents | `get_residents(addr_id)`, `get_all_residents()`, `add_resident()`, `update_resident()`, `delete_resident()`, `mark_deceased()`, `mark_left()`, `resident_exists()` |
| Events | `get_events_for_address(addr_id)`, `add_event()` |

`get_addresses()` fetches rows without SQL ordering and sorts in Python using `_address_sort_key()`,
which splits off the trailing building number (e.g. `"Шевченка 47"` → key `("шевченка", 47)`)
for correct Unicode-aware alphabetical + numeric ordering.

`init_db()` includes a migration block that safely adds new columns (`father`, `mother`, `spouse`)
to existing databases using `ALTER TABLE … ADD COLUMN` wrapped in `try/except`.

All functions open a fresh connection via `get_connection()`, use it as a context manager
(auto-commit / auto-close), and convert raw `sqlite3.Row` results into model objects via
`_row_to_resident()` and `_row_to_event()` helpers.

`PRAGMA foreign_keys = ON` is enabled on every connection so cascading deletes work correctly.

The `config` table stores one runtime key: `language` (`en` or `uk`).

### 5.4 `export.py` — Export / Import Module

| Function | Direction | Library |
|---|---|---|
| `export_csv(path, residents)` | Out — UTF-8 CSV with header row | `csv` (built-in) |
| `export_excel(path, residents)` | Out — `.xlsx` with styled header and auto-sized columns | `openpyxl` |
| `import_csv(path) → (new, skip)` | In — reads a previously exported CSV | `csv` (built-in) |
| `import_excel(path) → (new, skip)` | In — reads a previously exported `.xlsx` | `openpyxl` |

Export functions sort residents alphabetically by last name then first name. Column headers
and status values are rendered in the **currently active language** via `lang.get()`.

Import functions call `find_or_create_address()` and `resident_exists()` to avoid duplicates.
Both EN and UK status values are accepted via `_STATUS_MAP`.

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

- Real-time 🔍 search bar at the top; typing filters `_displayed` (subset of `_addresses`) in-place
- `tk.Listbox` with vertical scrollbar, displays `"  {street}  ({active_count})"`
- All listbox index operations use `_displayed` (filtered list), not the full `_addresses` list
- Active parishioner total at the bottom always sums across **all** addresses (not just filtered)
- Add / Edit / Delete buttons (labels from `lang.get()`)
- Double-click on an address opens the Edit dialog
- Selection change fires the `on_select` callback (injected from `MainWindow`) to update the right panel
- `refresh()` re-queries the database then calls `_apply_filter()` which restores selection by ID

### 5.7 `ui/resident_view.py` — Right Panel

`ResidentViewPanel(ttk.Frame)` is divided into two vertical sections:

**Top section — Residents table (`ttk.Treeview`)**

| Column | Content |
|---|---|
| Name | `full_name` |
| Date of Birth | `birth_date` displayed as DD.MM.YYYY |
| Baptized | `yes` / `no` (localized) |
| Married | `yes` / `no` (localized) |
| Status | `active` / `deceased` / `left` (localized; deceased = gray, left = blue `#5577bb`) |
| Date of Death | `death_date` displayed as DD.MM.YYYY; blank for active/left residents |

Real-time 🔍 name search bar above the table filters by `full_name` (first + last combined).

Action buttons: **+ Add Member**, **View**, **Edit**, **Record Event**, **Mark Deceased**, **Mark Left**, **Remove**
(all labels from `lang.get()`). The **View** button opens a read-only `ResidentViewDialog`.

**Bottom section — Event History (`tk.Text`, read-only)**

Chronological log of all events for all residents at the selected address, newest first.
Each line: `{DD.MM.YYYY}  {icon} {EVENT_TYPE}  {resident_name} — {description}`

Event icons: `★` birth, `✝` baptism, `♥` marriage, `✟` death

### 5.8 `ui/dialogs.py` — Modal Dialogs

All dialogs are `tk.Toplevel` with `grab_set()` (modal) and `transient(parent)`.
They store the result in `self.result` and destroy themselves; the caller inspects
`dlg.result` after `wait_window()` returns.

| Dialog | Purpose | Result type |
|---|---|---|
| `AddressDialog` | Add or edit an address | `Address` |
| `ResidentDialog` | Add or edit a resident (name, family, all date fields, notes) | `Resident` |
| `ResidentViewDialog` | Read-only summary of a resident | — (no result) |
| `MarkDeceasedDialog` | Quick death-date entry | `str` (ISO date) |
| `EventDialog` | Record any life event with type, date, description | `Event` |
| `LanguageDialog` | Select UI language (radio buttons) | `str` (lang code) |

All date fields use the shared `_date_entry(parent, label_key, row)` helper which creates
a labeled `ttk.Entry`, a clear (✕) button, and a DD.MM.YYYY format hint label.

Date input and display uses `DD.MM.YYYY`; storage uses ISO-8601 `YYYY-MM-DD`.
Conversion is handled by `_to_display(iso)` and `_to_iso(display)` module-level helpers.
Validation uses `^\d{2}\.\d{2}\.\d{4}$` via `_validate_date()`.

### 5.9 `install.py` — Cross-Platform Installer

Standalone Python script that runs the full installation sequence:

1. Checks Python version ≥ 3.8
2. Checks that `tkinter` is importable — prints OS-specific install instructions if missing
3. Runs `pip install openpyxl`
4. Calls `db.init_db()` to create `church.db` schema
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
│  father         TEXT     DEFAULT ''            │
│  mother         TEXT     DEFAULT ''            │
│  spouse         TEXT     DEFAULT ''            │
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
lexicographic ordering on text correctly sorts ISO dates. Dates are converted to `DD.MM.YYYY`
for display in the UI and back to ISO for storage, using `_to_display()` / `_to_iso()`.

**Event types** are always stored in English regardless of the active UI language.

**Schema migrations** are applied at startup by `init_db()` via `ALTER TABLE … ADD COLUMN`
(silently ignored if the column already exists), ensuring forward compatibility when
new fields are introduced.

---

## 7. Key Data Flows

### 7.1 Startup

```
main.py: MainWindow.__init__()
  │
  ├── db.init_db()                    → CREATE TABLE IF NOT EXISTS + column migrations
  ├── db.get_config('language')
  │     └── lang.set_lang(code)       → set active language before any UI is built
  ├── MainWindow._build_menu()        → all labels via lang.get()
  └── MainWindow._build_ui()
        ├── AddressListPanel(on_select=_on_address_selected)
        │     └── self.refresh() → db.get_addresses() → populate Listbox
        └── ResidentViewPanel(on_change=addr_panel.refresh) → _show_placeholder()
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
        │     └── dlg.result = Resident(father, mother, spouse, dates, ...)
        ├── db.add_resident(dlg.result)           → INSERT residents
        ├── if birth_date: db.add_event(birth)    → INSERT events (description via lang.get())
        ├── if death_date: db.add_event(death)    → INSERT events
        ├── _refresh_residents()                  → re-query + repopulate Treeview
        ├── _refresh_events()                     → re-query + repopulate log
        └── self._on_change()                     → AddressListPanel.refresh() (updates count)
```

### 7.4 Marking a Resident as Deceased

```
User selects resident, clicks "Mark Deceased"
  │
  └── ResidentViewPanel._mark_deceased()
        ├── guard: already deceased? → showinfo, return
        ├── MarkDeceasedDialog(parent, resident)  [modal — DD.MM.YYYY input]
        │     └── dlg.result = "YYYY-MM-DD"       (converted internally)
        ├── db.mark_deceased(res.id, date)        → UPDATE residents SET status='deceased', death_date=?
        ├── db.add_event(death_event)             → INSERT events
        ├── _refresh_residents()
        ├── _refresh_events()
        └── self._on_change()
```

### 7.5 Exporting to CSV / Excel

```
User: File → Export to CSV…
  │
  └── MainWindow._export_csv()
        ├── ensure backup/ directory exists (os.makedirs)
        ├── filedialog.asksaveasfilename(initialdir=backup/, initialfile=backup_<timestamp>.csv)
        ├── db.get_all_residents()
        └── export.export_csv(path, residents)

User: File → Export to Excel…
  │
  └── MainWindow._export_excel()
        ├── ensure xlsx-reports/ directory exists (os.makedirs)
        ├── filedialog.asksaveasfilename(initialdir=xlsx-reports/, initialfile=export_<timestamp>.xlsx)
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

### 7.6 Importing from CSV / Excel

```
User: File → Import from CSV… (or Excel…)
  │
  └── MainWindow._import_csv() / _import_excel()
        ├── filedialog.askopenfilename()
        └── export.import_csv(path) / import_excel(path)
              ├── read rows (skip header)
              ├── for each row:
              │     ├── find_or_create_address(street)
              │     ├── resident_exists(addr_id, first, last) → skip duplicate
              │     └── db.add_resident(Resident(...))
              └── return (new_count, skipped_count)
```

### 7.7 Changing Language

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
│  ADDRESSES       │  Maple Street 56               [right header]                     │
│  ──────────────  │  ─────────────────────────────────────────────────────────────    │
│  Cedar Rd   (3)  │  Name         DOB        Baptized Married Status   Date of Death  │
│  Church Ln  (3)  │  Maria Novak  14.09.1948  yes      yes    active                  │
│  Maple St   (2)  │  Peter Novak  07.06.1945  yes      yes    deceased 30.11.2021     │
│  Oak Ave    (2)  │  Thomas Novak 25.03.1970  yes      yes    active                  │
│                  │                                                                   │
│                  │  [+Add Member][View][Edit][Record Event][Mark Deceased][Remove]   │
│  [+Add][Edit]    │  ─────────────────────────────────────────────────────────────    │
│  [Delete]        │  Event History                                                    │
│                  │  30.11.2021  ✟ DEATH       Peter Novak passed away                │
│                  │  27.04.1968  ♥ MARRIAGE    Peter Novak married ...                │
│                  │  07.06.1945  ★ BIRTH       Peter Novak was born                   │
├──────────────────┴───────────────────────────────────────────────────────────────────┤
│  Viewing: Maple Street 56  •  2 active resident(s)   [status bar]                    │
└──────────────────────────────────────────────────────────────────────────────────────┘
```

Addresses in the left panel are sorted: alphabetically by street name (Unicode-aware,
supports Cyrillic), then numerically by building number within the same street.

The horizontal split is a `tk.PanedWindow` — the user can drag the divider.
Initial left panel width is 270 px; the right panel takes the remaining space.

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
| Date storage | ISO-8601 text `YYYY-MM-DD` | Sortable lexicographically; universally understood by import/export tools |
| Date display | `DD.MM.YYYY` | Familiar format for Ukrainian users; converted bidirectionally at UI boundary |
| Address sort | Python `str.casefold()` + regex | Correct Unicode/Cyrillic ordering; splitting trailing number enables numeric building-number sort |
| Modal dialogs | `tk.Toplevel` with `grab_set()` | Keeps all dialogs in the same process/window; `wait_window()` provides synchronous UX |

---

## 10. Constraints and Known Limitations

| Limitation | Detail |
|---|---|
| Single city | The city name (Kulykiv / Куликів) is hardcoded in `lang.py`. Multi-city use would require a schema change and UI for city management. |
| Language restart required | Language change takes effect only after restarting the app; the running UI is not rebuilt live. |
| No user authentication | Data is not protected — anyone with access to the PC can open the app or the `.db` file. |
| No backup / sync | No automatic backup. Users should manually copy `church.db` regularly. |
| No marriage linking | Spouse name is stored as free text per individual, not as a relation between two residents. |
| Date validation | Validates format (`DD.MM.YYYY`) but does not check calendar validity (e.g. `30.02.2024`). |
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
instructions if not), installs `openpyxl`, initialises the database schema, and creates
a launch shortcut (`run.sh` or `run.bat`). The app starts with an empty database.

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
| Multiple cities | Add a `cities` table; link `addresses` to a city; remove hardcoded city name |
| Dark mode | `ttk` themes can be swapped via `ttk.Style().theme_use('...')` |
| Calendar date picker | Replace free-text date entries with a calendar widget |
