# Parafiya Tserkvy Uspinnya Presvyatoyi Bohorodytsi — Kulykiv

A desktop application for tracking members of the church community,
grouped by home address. Record births, baptisms, marriages and deaths, keep
a full event history, and export your data to Excel or CSV at any time.

---

## Requirements

| Requirement | Detail |
|---|---|
| Operating system | Windows 10/11, Linux, macOS |
| Python | Version 3.8 or newer |
| tkinter | Included with Python on Windows and macOS; see below for Linux |
| Internet | Only needed once, to download the `openpyxl` package during installation |

---

## Installation

### Windows

1. Install Python from [python.org](https://www.python.org/downloads/)
   - During installation, check **"Add Python to PATH"**
2. Double-click **`install.bat`**
3. Follow the on-screen messages
4. When installation completes, press any key to launch the app

### Linux (Ubuntu / Debian)

Open a terminal in the `church_tracker` folder and run:

```bash
sudo apt install python3-tk     # install tkinter if not already present
bash install.sh
```

### macOS

Open a terminal in the `church_tracker` folder and run:

```bash
bash install.sh
```

> If tkinter is missing, reinstall Python from [python.org](https://www.python.org/downloads/)
> or run `brew install python-tk`

---

## Launching the App

After installation a launch shortcut is created automatically.

| Platform | Command |
|---|---|
| Windows | Double-click **`run.bat`** |
| Linux / macOS | Run `bash run.sh` in the terminal |
| Any platform | `python3 main.py` from the `church_tracker` folder |

---

## First Launch

The app starts with an empty database. Begin by adding your first address
in the left panel, then add residents to it.

---

## Interface Overview

The main window is split into two panels:

```
┌──────────────────┬──────────────────────────────────────────────┐
│  LEFT PANEL      │  RIGHT PANEL                                 │
│  Address list    │  Residents at the selected address           │
│                  │  + Event history log at the bottom           │
└──────────────────┴──────────────────────────────────────────────┘
```

### Left Panel — Addresses

- Lists all addresses sorted alphabetically by street name, then numerically by building number
- Shows the number of **active** (living) residents next to each address in brackets
- Click an address to view its residents on the right
- Double-click an address to edit it
- Use the **+ Add**, **Edit**, and **Delete** buttons to manage addresses

### Right Panel — Residents

The table shows all residents at the selected address:

| Column | Description |
|---|---|
| Name | Full name |
| Date of Birth | DD.MM.YYYY |
| Baptized | yes / no |
| Married | yes / no |
| Status | active / deceased |
| Date of Death | DD.MM.YYYY (blank if living) |

Deceased residents are shown in **gray**.

### Action Buttons

| Button | Action |
|---|---|
| **+ Add Member** | Add a new person to this address |
| **View** | Show a read-only summary of the selected person |
| **Edit** | Edit the selected person's details |
| **Record Event** | Log a baptism, marriage, birth, or death for the selected person |
| **Mark Deceased** | Quickly record the date of death for the selected person |
| **Remove** | Remove the selected person from the address (also deletes their event history) |

### Event History Log

The lower section of the right panel shows a chronological log of all life events
for everyone at the selected address, newest first.

Each entry shows:
- Date
- Event type icon (★ birth  ✝ baptism  ♥ marriage  ✟ death)
- Person's name
- Description (if provided)

---

## Adding a New Address

1. Click **+ Add** in the left panel
2. Enter the street address in **Street Name Number** format (e.g. `Church Lane 12` or `Шевченка 5`)
3. Optionally add a note (e.g. "corner house", "near the park")
4. Click **Save**

Addresses are sorted automatically: alphabetically by street name (supports both Latin
and Cyrillic), and numerically by building number within the same street.

---

## Adding a New Resident

1. Select the address in the left panel
2. Click **+ Add Member**
3. Fill in the details:
   - First name and last name (required)
   - Father (optional)
   - Mother (optional)
   - Husband / Wife (optional)
   - Date of birth (DD.MM.YYYY)
   - Date of baptism (DD.MM.YYYY)
   - Date of marriage (DD.MM.YYYY)
   - Date of death (DD.MM.YYYY) — only if the person has already passed away
   - Notes (optional)
4. Click **Save**

> **Date format:** All dates must be entered as `DD.MM.YYYY`
> (e.g. `15.06.1985` for 15 June 1985).
> Leave a field blank if the information is not known or not applicable.
> Use the **✕** button next to any date field to clear it.

---

## Viewing a Resident's Record

1. Select the person in the table
2. Click **View**

A read-only popup shows all stored details: name, family members, all dates, status,
and notes.

---

## Recording a Life Event

To add a baptism, marriage, or other event for an existing resident:

1. Select the address, then select the person in the table
2. Click **Record Event**
3. Choose the event type from the dropdown: birth, baptism, marriage, death
4. Enter the date (DD.MM.YYYY)
5. Optionally add a description
6. Click **Save**

> Recording a **baptism** or **marriage** event will automatically update the
> corresponding date on the person's record.
> Recording a **death** event will automatically mark the person as deceased.

---

## Marking a Person as Deceased

1. Select the address, then select the person in the table
2. Click **Mark Deceased**
3. Enter the date of death (DD.MM.YYYY)
4. Click **Confirm**

The person's status changes to *deceased*, their row turns gray, the date of death
appears in the table, and the event is added to the history log.

---

## Editing a Resident's Details

1. Select the person in the table
2. Click **Edit**
3. Update any fields
4. Click **Save**

---

## Exporting Data

Go to **File** in the menu bar:

| Option | Result |
|---|---|
| **Export to CSV…** | Saves all residents to a `.csv` file (opens in Excel, Notepad, etc.) |
| **Export to Excel…** | Saves all residents to a `.xlsx` Excel file with a styled header row |

You will be asked to choose a save location. The export includes all residents
from all addresses, sorted alphabetically by last name.

> **Note:** Excel export requires the `openpyxl` package. This is installed
> automatically by the installer. If you see an error, run `pip install openpyxl`.

---

## Importing Data

To populate the database from another machine, go to **File** in the menu bar:

| Option | Result |
|---|---|
| **Import from CSV…** | Reads residents from a previously exported `.csv` file |
| **Import from Excel…** | Reads residents from a previously exported `.xlsx` file |

The import matches the same column layout as the export. Addresses are created
automatically if they do not exist yet. Residents with the same name at the
same address are skipped (no duplicates). The status bar shows how many were
imported and how many were skipped.

**Tip — moving all data at once:** If you simply want to copy everything to
another machine (including the full event history), copy the `church.db` file
directly. That is the most complete backup method.

---

## Settings

### Change Language

Go to **Settings → Language / Мова…**, select **English** or **Українська**,
and click Save. The new language takes effect the next time you launch the app.

---

## Data Storage

All data is saved in the file **`church.db`** located in the same folder as the app.
This is a standard SQLite database file.

**Backup:** Simply copy `church.db` to a safe location (USB drive, cloud folder, etc.)
to back up all your data.

**Restore:** Replace `church.db` with your backup copy and restart the app.

---

## Building a Standalone Windows Executable

If you want to distribute the app to a computer without Python installed:

```bash
pip install pyinstaller
pyinstaller --onefile --windowed --name "ChurchTracker" main.py
```

The output file `dist/ChurchTracker.exe` can be copied to any Windows PC
and run without installing Python.

---

## Troubleshooting

| Problem | Solution |
|---|---|
| `ModuleNotFoundError: No module named 'tkinter'` | Linux: `sudo apt install python3-tk` |
| `No matching distribution found for tkinter` | tkinter cannot be installed via pip — use the system package manager (see above) |
| Excel export fails with "openpyxl is not installed" | Run `pip install openpyxl` |
| App does not start on Windows | Make sure Python is added to PATH; try running `python main.py` in a Command Prompt |
| Excel import fails with "openpyxl is not installed" | Run `pip install openpyxl` |
