import tkinter as tk
from tkinter import ttk, messagebox
from typing import Optional
from models import Address, Resident, Event
import database as db
import lang


def _date_entry(parent, label_key: str, row: int, initial: str = ""):
    """Helper: labeled date field with a clear button. label_key is a lang key."""
    ttk.Label(parent, text=lang.get(label_key)).grid(
        row=row, column=0, sticky="e", padx=8, pady=4
    )
    var = tk.StringVar(value=initial)
    ttk.Entry(parent, textvariable=var, width=14).grid(
        row=row, column=1, sticky="w", padx=4, pady=4
    )
    ttk.Button(
        parent, text="✕", width=2,
        command=lambda: var.set("")
    ).grid(row=row, column=2, sticky="w")
    ttk.Label(parent, text=lang.get("date_hint"), foreground="gray").grid(
        row=row, column=3, sticky="w", padx=4
    )
    return var


def _to_display(iso: str) -> str:
    """YYYY-MM-DD → DD.MM.YYYY for display in UI."""
    if iso and len(iso) == 10 and iso[4] == "-":
        return f"{iso[8:10]}.{iso[5:7]}.{iso[0:4]}"
    return iso


def _to_iso(display: str) -> str:
    """DD.MM.YYYY → YYYY-MM-DD for storage. Passes through existing ISO strings."""
    s = display.strip()
    if s and len(s) == 10 and s[2] == ".":
        return f"{s[6:10]}-{s[3:5]}-{s[0:2]}"
    return s


def _validate_date(value: str) -> bool:
    if not value:
        return True
    import re
    return bool(re.match(r"^\d{2}\.\d{2}\.\d{4}$", value))


# ── Address Dialog ────────────────────────────────────────────────────────────

class AddressDialog(tk.Toplevel):
    def __init__(self, parent, address: Optional[Address] = None):
        super().__init__(parent)
        self.result: Optional[Address] = None
        self.address = address

        self.title(lang.get("dlg_edit_address") if address else lang.get("dlg_add_address"))
        self.resizable(False, False)
        self.grab_set()
        self.transient(parent)

        frame = ttk.Frame(self, padding=16)
        frame.pack(fill="both", expand=True)

        ttk.Label(frame, text=lang.get("lbl_street")).grid(
            row=0, column=0, sticky="e", padx=8, pady=(6, 0)
        )
        self._street = tk.StringVar(value=address.street if address else "")
        ttk.Entry(frame, textvariable=self._street, width=34).grid(
            row=0, column=1, columnspan=3, sticky="ew", padx=4, pady=(6, 0)
        )
        ttk.Label(frame, text=lang.get("lbl_street_hint"),
                  foreground="gray", font=("", 8)).grid(
            row=1, column=1, columnspan=3, sticky="w", padx=4, pady=(0, 6)
        )

        ttk.Label(frame, text=lang.get("lbl_notes")).grid(
            row=2, column=0, sticky="ne", padx=8, pady=6
        )
        self._notes_text = tk.Text(frame, width=34, height=3)
        self._notes_text.grid(row=2, column=1, columnspan=3, sticky="ew", padx=4, pady=6)
        if address and address.notes:
            self._notes_text.insert("1.0", address.notes)

        btn_frame = ttk.Frame(frame)
        btn_frame.grid(row=3, column=0, columnspan=4, pady=8)
        ttk.Button(btn_frame, text=lang.get("save"),   command=self._save).pack(side="left", padx=6)
        ttk.Button(btn_frame, text=lang.get("cancel"), command=self.destroy).pack(side="left", padx=6)

        self.wait_window()

    def _save(self):
        street = self._street.get().strip()
        if not street:
            messagebox.showerror(lang.get("error"), lang.get("err_street_required"), parent=self)
            return
        notes = self._notes_text.get("1.0", "end-1c").strip()
        if self.address:
            self.address.street = street
            self.address.notes  = notes
            self.result = self.address
        else:
            self.result = Address(None, street, notes)
        self.destroy()


# ── Resident Dialog ───────────────────────────────────────────────────────────

class ResidentDialog(tk.Toplevel):
    def __init__(self, parent, address_id: int, resident: Optional[Resident] = None):
        super().__init__(parent)
        self.result: Optional[Resident] = None
        self.resident = resident
        self.address_id = address_id

        self.title(lang.get("dlg_edit_resident") if resident else lang.get("dlg_add_resident"))
        self.resizable(False, False)
        self.grab_set()
        self.transient(parent)

        frame = ttk.Frame(self, padding=16)
        frame.pack(fill="both", expand=True)

        row = 0
        ttk.Label(frame, text=lang.get("lbl_first_name")).grid(
            row=row, column=0, sticky="e", padx=8, pady=4
        )
        self._first = tk.StringVar(value=resident.first_name if resident else "")
        ttk.Entry(frame, textvariable=self._first, width=20).grid(
            row=row, column=1, sticky="w", padx=4, pady=4
        )

        row += 1
        ttk.Label(frame, text=lang.get("lbl_last_name")).grid(
            row=row, column=0, sticky="e", padx=8, pady=4
        )
        self._last = tk.StringVar(value=resident.last_name if resident else "")
        ttk.Entry(frame, textvariable=self._last, width=20).grid(
            row=row, column=1, sticky="w", padx=4, pady=4
        )

        row += 1
        ttk.Label(frame, text=lang.get("lbl_father")).grid(
            row=row, column=0, sticky="e", padx=8, pady=4
        )
        self._father = tk.StringVar(value=resident.father or "" if resident else "")
        ttk.Entry(frame, textvariable=self._father, width=26).grid(
            row=row, column=1, columnspan=3, sticky="w", padx=4, pady=4
        )

        row += 1
        ttk.Label(frame, text=lang.get("lbl_mother")).grid(
            row=row, column=0, sticky="e", padx=8, pady=4
        )
        self._mother = tk.StringVar(value=resident.mother or "" if resident else "")
        ttk.Entry(frame, textvariable=self._mother, width=26).grid(
            row=row, column=1, columnspan=3, sticky="w", padx=4, pady=4
        )

        row += 1
        ttk.Label(frame, text=lang.get("lbl_spouse")).grid(
            row=row, column=0, sticky="e", padx=8, pady=4
        )
        self._spouse = tk.StringVar(value=resident.spouse or "" if resident else "")
        ttk.Entry(frame, textvariable=self._spouse, width=26).grid(
            row=row, column=1, columnspan=3, sticky="w", padx=4, pady=4
        )

        row += 1
        self._birth    = _date_entry(frame, "lbl_dob",      row, _to_display(resident.birth_date    or "") if resident else "")
        row += 1
        self._baptism  = _date_entry(frame, "lbl_baptism",  row, _to_display(resident.baptism_date  or "") if resident else "")
        row += 1
        self._marriage = _date_entry(frame, "lbl_marriage", row, _to_display(resident.marriage_date or "") if resident else "")
        row += 1
        self._death    = _date_entry(frame, "lbl_death",    row, _to_display(resident.death_date    or "") if resident else "")

        row += 1
        ttk.Label(frame, text=lang.get("lbl_notes")).grid(
            row=row, column=0, sticky="ne", padx=8, pady=4
        )
        self._notes_text = tk.Text(frame, width=30, height=3)
        self._notes_text.grid(row=row, column=1, columnspan=3, sticky="ew", padx=4, pady=4)
        if resident and resident.notes:
            self._notes_text.insert("1.0", resident.notes)

        row += 1
        btn_frame = ttk.Frame(frame)
        btn_frame.grid(row=row, column=0, columnspan=4, pady=10)
        ttk.Button(btn_frame, text=lang.get("save"),   command=self._save).pack(side="left", padx=6)
        ttk.Button(btn_frame, text=lang.get("cancel"), command=self.destroy).pack(side="left", padx=6)

        self.wait_window()

    def _save(self):
        first = self._first.get().strip()
        last  = self._last.get().strip()
        if not first or not last:
            messagebox.showerror(lang.get("error"), lang.get("err_name_required"), parent=self)
            return

        date_fields = [
            ("lbl_dob",      self._birth),
            ("lbl_baptism",  self._baptism),
            ("lbl_marriage", self._marriage),
            ("lbl_death",    self._death),
        ]
        values = {}
        for label_key, var in date_fields:
            val = var.get().strip()
            if val and not _validate_date(val):
                messagebox.showerror(
                    lang.get("err_invalid_date"),
                    lang.get("err_date_format", field=lang.get(label_key).rstrip(":")),
                    parent=self,
                )
                return
            values[label_key] = _to_iso(val) if val else None

        notes  = self._notes_text.get("1.0", "end-1c").strip()
        death  = values["lbl_death"]
        status = "deceased" if death else (self.resident.status if self.resident else "active")
        father = self._father.get().strip() or None
        mother = self._mother.get().strip() or None
        spouse = self._spouse.get().strip() or None

        if self.resident:
            self.resident.first_name    = first
            self.resident.last_name     = last
            self.resident.birth_date    = values["lbl_dob"]
            self.resident.baptism_date  = values["lbl_baptism"]
            self.resident.marriage_date = values["lbl_marriage"]
            self.resident.death_date    = death
            self.resident.status        = status
            self.resident.father        = father
            self.resident.mother        = mother
            self.resident.spouse        = spouse
            self.resident.notes         = notes
            self.result = self.resident
        else:
            self.result = Resident(
                id=None,
                address_id=self.address_id,
                first_name=first,
                last_name=last,
                birth_date=values["lbl_dob"],
                baptism_date=values["lbl_baptism"],
                marriage_date=values["lbl_marriage"],
                death_date=death,
                status=status,
                father=father,
                mother=mother,
                spouse=spouse,
                notes=notes,
            )
        self.destroy()


# ── Resident View Dialog (read-only) ─────────────────────────────────────────

class ResidentViewDialog(tk.Toplevel):
    """Read-only summary of a single resident."""

    def __init__(self, parent, resident: Resident):
        super().__init__(parent)
        self.title(resident.full_name)
        self.resizable(False, False)
        self.grab_set()
        self.transient(parent)

        frame = ttk.Frame(self, padding=16)
        frame.pack(fill="both", expand=True)

        def row_label(r, label_key, value):
            ttk.Label(frame, text=lang.get(label_key),
                      foreground="gray").grid(row=r, column=0, sticky="e", padx=8, pady=3)
            ttk.Label(frame, text=value or "—").grid(
                row=r, column=1, sticky="w", padx=8, pady=3)

        if resident.status == "deceased":
            status_label = lang.get("status_deceased")
        elif resident.status == "left":
            status_label = lang.get("status_left")
        else:
            status_label = lang.get("status_active")

        row_label(0, "lbl_first_name", resident.first_name)
        row_label(1, "lbl_last_name",  resident.last_name)
        row_label(2, "lbl_father",     resident.father or "")
        row_label(3, "lbl_mother",     resident.mother or "")
        row_label(4, "lbl_spouse",     resident.spouse or "")
        row_label(5, "lbl_dob",        _to_display(resident.birth_date    or ""))
        row_label(6, "lbl_baptism",    _to_display(resident.baptism_date  or ""))
        row_label(7, "lbl_marriage",   _to_display(resident.marriage_date or ""))
        row_label(8, "lbl_death",      _to_display(resident.death_date    or ""))
        ttk.Label(frame, text=lang.get("col_status"),
                  foreground="gray").grid(row=9, column=0, sticky="e", padx=8, pady=3)
        ttk.Label(frame, text=status_label).grid(row=9, column=1, sticky="w", padx=8, pady=3)

        if resident.notes:
            ttk.Separator(frame, orient="horizontal").grid(
                row=10, column=0, columnspan=2, sticky="ew", pady=6)
            ttk.Label(frame, text=lang.get("lbl_notes"),
                      foreground="gray").grid(row=11, column=0, sticky="ne", padx=8, pady=3)
            ttk.Label(frame, text=resident.notes, wraplength=260,
                      justify="left").grid(row=11, column=1, sticky="w", padx=8, pady=3)

        ttk.Button(frame, text=lang.get("cancel"),
                   command=self.destroy).grid(
            row=12, column=0, columnspan=2, pady=(12, 0))

        self.wait_window()


# ── Mark Deceased Dialog ──────────────────────────────────────────────────────

class MarkDeceasedDialog(tk.Toplevel):
    def __init__(self, parent, resident: Resident):
        super().__init__(parent)
        self.result: Optional[str] = None
        self.title(lang.get("dlg_mark_deceased", name=resident.full_name))
        self.resizable(False, False)
        self.grab_set()
        self.transient(parent)

        frame = ttk.Frame(self, padding=16)
        frame.pack(fill="both", expand=True)

        ttk.Label(frame,
                  text=lang.get("lbl_recording_death", name=resident.full_name),
                  font=("", 10, "bold")).grid(row=0, column=0, columnspan=4, pady=(0, 10))

        self._death_date = _date_entry(frame, "lbl_death", 1)

        btn_frame = ttk.Frame(frame)
        btn_frame.grid(row=2, column=0, columnspan=4, pady=10)
        ttk.Button(btn_frame, text=lang.get("confirm"), command=self._save).pack(side="left", padx=6)
        ttk.Button(btn_frame, text=lang.get("cancel"),  command=self.destroy).pack(side="left", padx=6)

        self.wait_window()

    def _save(self):
        date = self._death_date.get().strip()
        if not date:
            messagebox.showerror(lang.get("error"),
                                 lang.get("err_death_date_required"), parent=self)
            return
        if not _validate_date(date):
            messagebox.showerror(lang.get("err_invalid_date"),
                                 lang.get("err_date_format",
                                          field=lang.get("lbl_death").rstrip(":")),
                                 parent=self)
            return
        self.result = _to_iso(date)
        self.destroy()


# ── Event Dialog ──────────────────────────────────────────────────────────────

class EventDialog(tk.Toplevel):
    def __init__(self, parent, resident: Resident):
        super().__init__(parent)
        self.result: Optional[Event] = None
        self.resident = resident
        self.title(lang.get("dlg_record_event", name=resident.full_name))
        self.resizable(False, False)
        self.grab_set()
        self.transient(parent)

        frame = ttk.Frame(self, padding=16)
        frame.pack(fill="both", expand=True)

        ttk.Label(frame,
                  text=lang.get("lbl_resident", name=resident.full_name),
                  font=("", 10, "bold")).grid(row=0, column=0, columnspan=4, pady=(0, 8))

        ttk.Label(frame, text=lang.get("lbl_event_type")).grid(
            row=1, column=0, sticky="e", padx=8, pady=4
        )
        # Store localized labels; we'll convert back to EN key on save
        self._event_labels = lang.event_types()
        self._event_type_var = tk.StringVar(value=self._event_labels[1])  # default: baptism
        ttk.Combobox(
            frame, textvariable=self._event_type_var,
            values=self._event_labels, state="readonly", width=18
        ).grid(row=1, column=1, sticky="w", padx=4, pady=4)

        self._event_date = _date_entry(frame, "lbl_event_date", 2)

        ttk.Label(frame, text=lang.get("lbl_description")).grid(
            row=3, column=0, sticky="ne", padx=8, pady=4
        )
        self._desc_text = tk.Text(frame, width=30, height=3)
        self._desc_text.grid(row=3, column=1, columnspan=3, sticky="ew", padx=4, pady=4)

        btn_frame = ttk.Frame(frame)
        btn_frame.grid(row=4, column=0, columnspan=4, pady=10)
        ttk.Button(btn_frame, text=lang.get("save"),   command=self._save).pack(side="left", padx=6)
        ttk.Button(btn_frame, text=lang.get("cancel"), command=self.destroy).pack(side="left", padx=6)

        self.wait_window()

    def _save(self):
        localized_type = self._event_type_var.get()
        event_type = lang.event_type_to_key(localized_type)  # store EN key in DB
        date = self._event_date.get().strip()
        if not date:
            messagebox.showerror(lang.get("error"),
                                 lang.get("err_event_date_required"), parent=self)
            return
        if not _validate_date(date):
            messagebox.showerror(lang.get("err_invalid_date"),
                                 lang.get("err_date_format",
                                          field=lang.get("lbl_event_date").rstrip(":")),
                                 parent=self)
            return
        desc = self._desc_text.get("1.0", "end-1c").strip()
        self.result = Event(
            id=None,
            resident_id=self.resident.id,
            event_type=event_type,
            event_date=_to_iso(date),
            description=desc,
        )
        self.destroy()


# ── City Dialog ───────────────────────────────────────────────────────────────

class CityDialog(tk.Toplevel):
    def __init__(self, parent, current_city: str = ""):
        super().__init__(parent)
        self.result: Optional[str] = None
        self.title(lang.get("dlg_city"))
        self.resizable(False, False)
        self.grab_set()
        self.transient(parent)

        frame = ttk.Frame(self, padding=16)
        frame.pack(fill="both", expand=True)

        ttk.Label(frame, text=lang.get("lbl_city")).grid(
            row=0, column=0, sticky="e", padx=8, pady=8
        )
        self._city = tk.StringVar(value=current_city)
        ttk.Entry(frame, textvariable=self._city, width=28).grid(
            row=0, column=1, sticky="w", padx=4, pady=8
        )

        btn_frame = ttk.Frame(frame)
        btn_frame.grid(row=1, column=0, columnspan=2, pady=8)
        ttk.Button(btn_frame, text=lang.get("save"),   command=self._save).pack(side="left", padx=6)
        ttk.Button(btn_frame, text=lang.get("cancel"), command=self.destroy).pack(side="left", padx=6)

        self.wait_window()

    def _save(self):
        city = self._city.get().strip()
        if not city:
            messagebox.showerror(lang.get("error"), lang.get("err_city_required"), parent=self)
            return
        self.result = city
        self.destroy()


# ── Language Dialog ───────────────────────────────────────────────────────────

class LanguageDialog(tk.Toplevel):
    def __init__(self, parent, current_lang: str = "en"):
        super().__init__(parent)
        self.result: Optional[str] = None
        self.title(lang.get("dlg_language"))
        self.resizable(False, False)
        self.grab_set()
        self.transient(parent)

        frame = ttk.Frame(self, padding=20)
        frame.pack(fill="both", expand=True)

        self._lang_var = tk.StringVar(value=current_lang)
        for code, name in lang.SUPPORTED.items():
            ttk.Radiobutton(
                frame, text=name, variable=self._lang_var, value=code
            ).pack(anchor="w", pady=4)

        ttk.Label(frame, text=lang.get("lang_restart_note"),
                  foreground="gray", wraplength=220).pack(pady=(10, 4))

        btn_frame = ttk.Frame(frame)
        btn_frame.pack(pady=8)
        ttk.Button(btn_frame, text=lang.get("save"),   command=self._save).pack(side="left", padx=6)
        ttk.Button(btn_frame, text=lang.get("cancel"), command=self.destroy).pack(side="left", padx=6)

        self.wait_window()

    def _save(self):
        self.result = self._lang_var.get()
        self.destroy()
