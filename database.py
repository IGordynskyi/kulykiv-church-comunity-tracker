import sqlite3
import os
import re as _re
from typing import List, Optional
from models import Address, Resident, Event

DB_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "church.db")


def get_connection():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON")
    return conn


def init_db():
    with get_connection() as conn:
        conn.executescript("""
            CREATE TABLE IF NOT EXISTS config (
                key   TEXT PRIMARY KEY,
                value TEXT
            );

            CREATE TABLE IF NOT EXISTS addresses (
                id     INTEGER PRIMARY KEY AUTOINCREMENT,
                street TEXT NOT NULL,
                notes  TEXT DEFAULT ''
            );

            CREATE TABLE IF NOT EXISTS residents (
                id             INTEGER PRIMARY KEY AUTOINCREMENT,
                address_id     INTEGER NOT NULL REFERENCES addresses(id) ON DELETE CASCADE,
                first_name     TEXT NOT NULL,
                last_name      TEXT NOT NULL,
                birth_date     TEXT,
                baptism_date   TEXT,
                marriage_date  TEXT,
                death_date     TEXT,
                status         TEXT NOT NULL DEFAULT 'active',
                father         TEXT DEFAULT '',
                mother         TEXT DEFAULT '',
                spouse         TEXT DEFAULT '',
                notes          TEXT DEFAULT ''
            );

            CREATE TABLE IF NOT EXISTS events (
                id           INTEGER PRIMARY KEY AUTOINCREMENT,
                resident_id  INTEGER NOT NULL REFERENCES residents(id) ON DELETE CASCADE,
                event_type   TEXT NOT NULL,
                event_date   TEXT NOT NULL,
                description  TEXT DEFAULT '',
                created_at   TEXT DEFAULT (datetime('now'))
            );
        """)
        # Migration: add columns that may be absent in older databases
        import sqlite3 as _sqlite3
        for col in ("father", "mother", "spouse"):
            try:
                conn.execute(f"ALTER TABLE residents ADD COLUMN {col} TEXT DEFAULT ''")
            except _sqlite3.OperationalError:
                pass  # column already exists


# ── Config ──────────────────────────────────────────────────────────────────

def get_config(key: str, default: str = "") -> str:
    with get_connection() as conn:
        row = conn.execute("SELECT value FROM config WHERE key=?", (key,)).fetchone()
        return row["value"] if row else default


def set_config(key: str, value: str):
    with get_connection() as conn:
        conn.execute("INSERT OR REPLACE INTO config VALUES (?,?)", (key, value))


# ── Addresses ────────────────────────────────────────────────────────────────

def _address_sort_key(street: str):
    """Return (street_name_casefold, building_number) for natural sort.

    Handles 'Street Name 12', 'вул. Незалежності 15', etc.
    Addresses without a trailing number sort as building 0.
    """
    m = _re.match(r'^(.*?)\s+(\d+)\s*$', street.strip())
    if m:
        return (m.group(1).casefold(), int(m.group(2)))
    return (street.strip().casefold(), 0)


def get_addresses() -> List[Address]:
    with get_connection() as conn:
        rows = conn.execute("""
            SELECT a.id, a.street, a.notes,
                   COUNT(CASE WHEN r.status='active' THEN 1 END) AS active_count
            FROM addresses a
            LEFT JOIN residents r ON r.address_id = a.id
            GROUP BY a.id
        """).fetchall()
        result = [Address(r["id"], r["street"], r["notes"], r["active_count"]) for r in rows]
        result.sort(key=lambda a: _address_sort_key(a.street))
        return result


def add_address(street: str, notes: str = "") -> Address:
    with get_connection() as conn:
        cur = conn.execute(
            "INSERT INTO addresses (street, notes) VALUES (?,?)", (street, notes)
        )
        return Address(cur.lastrowid, street, notes)


def update_address(addr: Address):
    with get_connection() as conn:
        conn.execute(
            "UPDATE addresses SET street=?, notes=? WHERE id=?",
            (addr.street, addr.notes, addr.id),
        )


def delete_address(addr_id: int):
    with get_connection() as conn:
        conn.execute("DELETE FROM addresses WHERE id=?", (addr_id,))


def find_or_create_address(street: str) -> int:
    """Return address id matching street (case-insensitive); create if absent."""
    street = street.strip()
    with get_connection() as conn:
        row = conn.execute(
            "SELECT id FROM addresses WHERE LOWER(street)=LOWER(?)", (street,)
        ).fetchone()
        if row:
            return row["id"]
        cur = conn.execute("INSERT INTO addresses (street) VALUES (?)", (street,))
        return cur.lastrowid


def resident_exists(address_id: int, first_name: str, last_name: str) -> bool:
    """Return True if a resident with the same name already lives at address_id."""
    with get_connection() as conn:
        row = conn.execute(
            """SELECT id FROM residents
               WHERE address_id=?
                 AND LOWER(first_name)=LOWER(?)
                 AND LOWER(last_name)=LOWER(?)""",
            (address_id, first_name.strip(), last_name.strip()),
        ).fetchone()
        return row is not None


# ── Residents ────────────────────────────────────────────────────────────────

def get_residents(address_id: int) -> List[Resident]:
    with get_connection() as conn:
        rows = conn.execute(
            "SELECT * FROM residents WHERE address_id=? ORDER BY last_name, first_name",
            (address_id,),
        ).fetchall()
        return [_row_to_resident(r) for r in rows]


def get_all_residents() -> List[Resident]:
    with get_connection() as conn:
        rows = conn.execute(
            "SELECT * FROM residents ORDER BY last_name, first_name"
        ).fetchall()
        return [_row_to_resident(r) for r in rows]


def add_resident(res: Resident) -> Resident:
    with get_connection() as conn:
        cur = conn.execute(
            """INSERT INTO residents
               (address_id, first_name, last_name, birth_date, baptism_date,
                marriage_date, death_date, status, father, mother, spouse, notes)
               VALUES (?,?,?,?,?,?,?,?,?,?,?,?)""",
            (res.address_id, res.first_name, res.last_name, res.birth_date,
             res.baptism_date, res.marriage_date, res.death_date, res.status,
             res.father or "", res.mother or "", res.spouse or "", res.notes),
        )
        res.id = cur.lastrowid
        return res


def update_resident(res: Resident):
    with get_connection() as conn:
        conn.execute(
            """UPDATE residents SET
               first_name=?, last_name=?, birth_date=?, baptism_date=?,
               marriage_date=?, death_date=?, status=?,
               father=?, mother=?, spouse=?, notes=?
               WHERE id=?""",
            (res.first_name, res.last_name, res.birth_date, res.baptism_date,
             res.marriage_date, res.death_date, res.status,
             res.father or "", res.mother or "", res.spouse or "", res.notes, res.id),
        )


def delete_resident(res_id: int):
    with get_connection() as conn:
        conn.execute("DELETE FROM residents WHERE id=?", (res_id,))


def mark_deceased(res_id: int, death_date: str):
    with get_connection() as conn:
        conn.execute(
            "UPDATE residents SET status='deceased', death_date=? WHERE id=?",
            (death_date, res_id),
        )


def mark_left(res_id: int):
    with get_connection() as conn:
        conn.execute(
            "UPDATE residents SET status='left' WHERE id=?",
            (res_id,),
        )


# ── Events ───────────────────────────────────────────────────────────────────

def get_events_for_address(address_id: int) -> List[Event]:
    with get_connection() as conn:
        rows = conn.execute(
            """SELECT e.*, r.first_name || ' ' || r.last_name AS resident_name
               FROM events e
               JOIN residents r ON r.id = e.resident_id
               WHERE r.address_id = ?
               ORDER BY e.event_date DESC, e.id DESC""",
            (address_id,),
        ).fetchall()
        return [_row_to_event(r) for r in rows]


def add_event(event: Event) -> Event:
    with get_connection() as conn:
        cur = conn.execute(
            "INSERT INTO events (resident_id, event_type, event_date, description) VALUES (?,?,?,?)",
            (event.resident_id, event.event_type, event.event_date, event.description),
        )
        event.id = cur.lastrowid
        return event


# ── Helpers ──────────────────────────────────────────────────────────────────

def _row_to_resident(r) -> Resident:
    keys = r.keys()
    return Resident(
        id=r["id"],
        address_id=r["address_id"],
        first_name=r["first_name"],
        last_name=r["last_name"],
        birth_date=r["birth_date"],
        baptism_date=r["baptism_date"],
        marriage_date=r["marriage_date"],
        death_date=r["death_date"],
        status=r["status"],
        father=r["father"] or None if "father" in keys else None,
        mother=r["mother"] or None if "mother" in keys else None,
        spouse=r["spouse"] or None if "spouse" in keys else None,
        notes=r["notes"] or "",
    )


def _row_to_event(r) -> Event:
    return Event(
        id=r["id"],
        resident_id=r["resident_id"],
        event_type=r["event_type"],
        event_date=r["event_date"],
        description=r["description"] or "",
        created_at=r["created_at"] or "",
        resident_name=r["resident_name"] if "resident_name" in r.keys() else "",
    )
