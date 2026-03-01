# Church Community Tracker
### Parafiya Tserkvy Uspinnya Presvyatoyi Bohorodytsi — Kulykiv

A standalone desktop application for maintaining the register of a church community.
Residents are organised by home address. The app tracks personal milestones (birth,
baptism, marriage, death), family relationships, and a chronological event history per
household. Data can be exported to CSV or Excel at any time.

The interface is available in **English** and **Ukrainian**.

---

## Quick Start

### 1. Install

| Platform | Command |
|---|---|
| Windows | Double-click `install.bat` |
| Linux | `bash install.sh` |
| macOS | `bash install.sh` |

**Requires Python 3.8+** and `tkinter` (bundled with Python on Windows and macOS;
on Linux run `sudo apt install python3-tk` first).

### 2. Launch

| Platform | Command |
|---|---|
| Windows | Double-click `run.bat` |
| Linux / macOS | `bash run.sh` |
| Any platform | `python3 main.py` |

---

## Documentation

| Document | Description |
|---|---|
| [User Guide (English)](doc/USER_GUIDE.EN.md) | Full instructions for installing, launching, and using the application |
| [Посібник користувача (Українська)](doc/USER_GUIDE.UA.md) | Повні інструкції з встановлення та використання застосунку |
| [High-Level Design (HLD)](doc/HLD.md) | Architecture, module descriptions, data flows, database schema, and technology decisions |
| [Testing Guide](doc/TESTING.md) | How to run the automated test suite and a description of every test |

---

## Data

All data is stored locally in **`church.db`** (SQLite), created automatically on first launch.

**Backup:** copy `church.db` to a safe location.
**Restore:** replace `church.db` with the backup and restart the app.
