import tkinter as tk
from tkinter import ttk, messagebox
from typing import Optional, List
from models import Address, Resident, Event
import database as db
import lang
from ui.dialogs import ResidentDialog, ResidentViewDialog, MarkDeceasedDialog, EventDialog
from transliterate import normalize_for_search


def _fmt_date(iso: str) -> str:
    """YYYY-MM-DD → DD.MM.YYYY for display."""
    if iso and len(iso) == 10 and iso[4] == "-":
        return f"{iso[8:10]}.{iso[5:7]}.{iso[0:4]}"
    return iso


_EVENT_ICONS = {
    "birth":    "★",
    "baptism":  "✝",
    "marriage": "♥",
    "death":    "✟",
}


class ResidentViewPanel(ttk.Frame):
    """Right panel: residents table + event history for the selected address."""

    def __init__(self, parent, on_change=None):
        super().__init__(parent)
        self._address: Optional[Address] = None
        self._residents: List[Resident] = []
        self._on_change = on_change or (lambda: None)
        self._name_filter_var = tk.StringVar()  # created before _build_ui wires the trace
        self._build_ui()
        self._show_placeholder()

    def _build_ui(self):
        # ── Header ──────────────────────────────────────────────────────────
        self._header_var = tk.StringVar(value=lang.get("select_address_placeholder"))
        header = ttk.Label(self, textvariable=self._header_var, font=("", 12, "bold"))
        header.pack(fill="x", padx=10, pady=(8, 4))

        ttk.Separator(self, orient="horizontal").pack(fill="x", padx=8)

        # ── Name search bar ──────────────────────────────────────────────────
        sf = ttk.Frame(self)
        sf.pack(fill="x", padx=8, pady=(6, 0))
        ttk.Label(sf, text="🔍", font=("", 9)).pack(side="left")
        self._name_filter_var.trace_add("write", lambda *_: self._apply_name_filter())
        ttk.Entry(sf, textvariable=self._name_filter_var,
                  font=("", 9)).pack(side="left", fill="x", expand=True, padx=(4, 2))
        ttk.Button(sf, text="✕", width=2,
                   command=lambda: self._name_filter_var.set("")).pack(side="left")

        # ── Residents table ──────────────────────────────────────────────────
        res_frame = ttk.Frame(self)
        res_frame.pack(fill="both", expand=True, padx=8, pady=4)

        columns = ("name", "dob", "baptized", "married", "status", "dod")
        self._tree = ttk.Treeview(
            res_frame,
            columns=columns,
            show="headings",
            selectmode="browse",
            height=10,
        )
        self._tree.heading("name",     text=lang.get("col_name"))
        self._tree.heading("dob",      text=lang.get("col_dob"))
        self._tree.heading("baptized", text=lang.get("col_baptized"))
        self._tree.heading("married",  text=lang.get("col_married"))
        self._tree.heading("status",   text=lang.get("col_status"))
        self._tree.heading("dod",      text=lang.get("col_dod"))

        self._tree.column("name",     width=160, minwidth=120)
        self._tree.column("dob",      width=105, minwidth=90,  anchor="center")
        self._tree.column("baptized", width=70,  minwidth=60,  anchor="center")
        self._tree.column("married",  width=70,  minwidth=60,  anchor="center")
        self._tree.column("status",   width=80,  minwidth=60,  anchor="center")
        self._tree.column("dod",      width=105, minwidth=90,  anchor="center")

        vsb = ttk.Scrollbar(res_frame, orient="vertical", command=self._tree.yview)
        self._tree.configure(yscrollcommand=vsb.set)
        vsb.pack(side="right", fill="y")
        self._tree.pack(side="left", fill="both", expand=True)

        # Tag for deceased (gray text) and left (blue text)
        self._tree.tag_configure("deceased", foreground="gray")
        self._tree.tag_configure("left", foreground="#5577bb")

        # ── Action buttons ───────────────────────────────────────────────────
        btn_frame = ttk.Frame(self)
        btn_frame.pack(fill="x", padx=8, pady=4)
        self._btn_add    = ttk.Button(btn_frame, text=lang.get("btn_add_member"),   command=self._add_resident)
        self._btn_view   = ttk.Button(btn_frame, text=lang.get("btn_view"),         command=self._view_resident)
        self._btn_edit   = ttk.Button(btn_frame, text=lang.get("btn_edit"),         command=self._edit_resident)
        self._btn_event  = ttk.Button(btn_frame, text=lang.get("btn_record_event"), command=self._record_event)
        self._btn_death  = ttk.Button(btn_frame, text=lang.get("btn_mark_deceased"),command=self._mark_deceased)
        self._btn_left   = ttk.Button(btn_frame, text=lang.get("btn_mark_left"),    command=self._mark_left)
        self._btn_delete = ttk.Button(btn_frame, text=lang.get("btn_remove"),       command=self._delete_resident)
        for btn in (self._btn_add, self._btn_view, self._btn_edit, self._btn_event,
                    self._btn_death, self._btn_left, self._btn_delete):
            btn.pack(side="left", padx=3)

        ttk.Separator(self, orient="horizontal").pack(fill="x", padx=8, pady=(4, 0))

        # ── Event history ────────────────────────────────────────────────────
        ttk.Label(self, text=lang.get("event_history"),
                  font=("", 9, "bold")).pack(anchor="w", padx=10, pady=(4, 2))

        log_frame = ttk.Frame(self)
        log_frame.pack(fill="both", expand=True, padx=8, pady=(0, 8))

        log_vsb = ttk.Scrollbar(log_frame, orient="vertical")
        self._log = tk.Text(
            log_frame,
            state="disabled",
            height=7,
            font=("Courier", 9),
            relief="flat",
            background="#f8f8f8",
            yscrollcommand=log_vsb.set,
        )
        log_vsb.config(command=self._log.yview)
        log_vsb.pack(side="right", fill="y")
        self._log.pack(side="left", fill="both", expand=True)

    def _show_placeholder(self):
        self._header_var.set(lang.get("select_address_placeholder"))
        self._tree.delete(*self._tree.get_children())
        self._set_log("")
        self._set_buttons_state("disabled")

    def _set_buttons_state(self, state: str):
        for btn in (self._btn_add, self._btn_view, self._btn_edit, self._btn_event,
                    self._btn_death, self._btn_left, self._btn_delete):
            btn.config(state=state)

    def load_address(self, address: Optional[Address]):
        self._address = address
        if address is None:
            self._set_log("")
            self._apply_name_filter()  # shows global search if filter active, else placeholder
            return
        self._header_var.set(address.street)
        self._set_buttons_state("normal")
        self._refresh_residents()
        self._refresh_events()

    def _refresh_residents(self):
        if not self._address:
            # Re-run global search if one is active, otherwise just clear
            self._apply_name_filter()
            return
        self._residents = db.get_residents(self._address.id)
        self._apply_name_filter()

    def _apply_name_filter(self):
        q = normalize_for_search(self._name_filter_var.get().strip())
        if self._address is None:
            if q:
                self._global_search(q)
            else:
                # No address, no filter → full placeholder state
                self._tree.delete(*self._tree.get_children())
                self._residents = []
                self._header_var.set(lang.get("select_address_placeholder"))
                self._set_buttons_state("disabled")
            return
        # Normal mode: filter within the selected address
        self._tree.delete(*self._tree.get_children())
        for r in self._residents:
            if q and q not in normalize_for_search(r.full_name):
                continue
            self._insert_resident_row(r, r.full_name)

    def _insert_resident_row(self, r, name_text: str):
        """Insert a single resident into the treeview."""
        if r.status == "deceased":
            tag = "deceased"
            status_label = lang.get("status_deceased")
        elif r.status == "left":
            tag = "left"
            status_label = lang.get("status_left")
        else:
            tag = ""
            status_label = lang.get("status_active")
        self._tree.insert(
            "", "end",
            iid=str(r.id),
            values=(
                name_text,
                _fmt_date(r.birth_date or ""),
                lang.get("yes") if r.is_baptized else lang.get("no"),
                lang.get("yes") if r.is_married  else lang.get("no"),
                status_label,
                _fmt_date(r.death_date or ""),
            ),
            tags=(tag,),
        )

    def _global_search(self, q: str):
        """Search all residents by name across all addresses."""
        all_res = db.get_all_residents()
        addr_map = {a.id: a.street for a in db.get_addresses()}
        matches = [r for r in all_res if q in normalize_for_search(r.full_name)]
        self._residents = matches
        self._tree.delete(*self._tree.get_children())
        if matches:
            self._header_var.set(lang.get("search_results_header"))
            # Enable action buttons; Add Member requires a selected address
            for btn in (self._btn_view, self._btn_edit, self._btn_event,
                        self._btn_death, self._btn_left, self._btn_delete):
                btn.config(state="normal")
            self._btn_add.config(state="disabled")
            for r in matches:
                street = addr_map.get(r.address_id, "")
                self._insert_resident_row(r, f"{r.full_name}  —  {street}")
        else:
            self._header_var.set(lang.get("select_address_placeholder"))
            self._set_buttons_state("disabled")

    def _refresh_events(self):
        if not self._address:
            self._set_log("")
            return
        events = db.get_events_for_address(self._address.id)
        if not events:
            self._set_log(lang.get("no_events"))
            return
        lines = []
        for e in events:
            icon  = _EVENT_ICONS.get(e.event_type, "•")
            label = lang.event_key_to_label(e.event_type).upper()
            desc  = f" — {e.description}" if e.description else ""
            lines.append(f"{_fmt_date(e.event_date)}  {icon} {label:12s}  {e.resident_name}{desc}")
        self._set_log("\n".join(lines))

    def _set_log(self, text: str):
        self._log.config(state="normal")
        self._log.delete("1.0", "end")
        self._log.insert("1.0", text)
        self._log.config(state="disabled")

    def _selected_resident(self) -> Optional[Resident]:
        sel = self._tree.selection()
        if not sel:
            return None
        res_id = int(sel[0])
        for r in self._residents:
            if r.id == res_id:
                return r
        return None

    def _view_resident(self):
        res = self._selected_resident()
        if not res:
            messagebox.showinfo(lang.get("info"),
                                lang.get("select_resident_first"), parent=self)
            return
        ResidentViewDialog(self, res)

    def _add_resident(self):
        if not self._address:
            return
        dlg = ResidentDialog(self, self._address.id)
        if dlg.result:
            r = db.add_resident(dlg.result)
            if r.birth_date:
                db.add_event(Event(
                    None, r.id, "birth", r.birth_date,
                    lang.get("auto_born", name=r.full_name)
                ))
            if r.death_date:
                db.add_event(Event(
                    None, r.id, "death", r.death_date,
                    lang.get("auto_died", name=r.full_name)
                ))
            self._refresh_residents()
            self._refresh_events()
            self._on_change()

    def _edit_resident(self):
        res = self._selected_resident()
        if not res:
            messagebox.showinfo(lang.get("info"),
                                lang.get("select_resident_first"), parent=self)
            return
        dlg = ResidentDialog(self, res.address_id, res)
        if dlg.result:
            db.update_resident(dlg.result)
            self._refresh_residents()
            self._refresh_events()
            self._on_change()

    def _record_event(self):
        res = self._selected_resident()
        if not res:
            messagebox.showinfo(lang.get("info"),
                                lang.get("select_resident_first"), parent=self)
            return
        dlg = EventDialog(self, res)
        if dlg.result:
            event = db.add_event(dlg.result)
            if event.event_type == "baptism" and not res.baptism_date:
                res.baptism_date = event.event_date
                db.update_resident(res)
            elif event.event_type == "marriage" and not res.marriage_date:
                res.marriage_date = event.event_date
                db.update_resident(res)
            elif event.event_type == "death":
                if res.status == "deceased":
                    messagebox.showinfo(lang.get("already_deceased"),
                                        lang.get("already_deceased_msg", name=res.full_name),
                                        parent=self)
                    return
                db.mark_deceased(res.id, event.event_date)
            self._refresh_residents()
            self._refresh_events()
            self._on_change()

    def _mark_deceased(self):
        res = self._selected_resident()
        if not res:
            messagebox.showinfo(lang.get("info"),
                                lang.get("select_resident_first"), parent=self)
            return
        if res.status == "deceased":
            messagebox.showinfo(lang.get("already_deceased"),
                                lang.get("already_deceased_msg", name=res.full_name),
                                parent=self)
            return
        dlg = MarkDeceasedDialog(self, res)
        if dlg.result:
            db.mark_deceased(res.id, dlg.result)
            db.add_event(Event(
                None, res.id, "death", dlg.result,
                lang.get("auto_died", name=res.full_name)
            ))
            self._refresh_residents()
            self._refresh_events()
            self._on_change()

    def _mark_left(self):
        res = self._selected_resident()
        if not res:
            messagebox.showinfo(lang.get("info"),
                                lang.get("select_resident_first"), parent=self)
            return
        if res.status == "left":
            messagebox.showinfo(lang.get("already_left"),
                                lang.get("already_left_msg", name=res.full_name),
                                parent=self)
            return
        if res.status == "deceased":
            messagebox.showinfo(lang.get("already_deceased"),
                                lang.get("already_deceased_msg", name=res.full_name),
                                parent=self)
            return
        if not messagebox.askyesno(
            lang.get("btn_mark_left"),
            lang.get("confirm_mark_left", name=res.full_name),
            parent=self,
        ):
            return
        db.mark_left(res.id)
        self._refresh_residents()
        self._on_change()

    def _delete_resident(self):
        res = self._selected_resident()
        if not res:
            messagebox.showinfo(lang.get("info"),
                                lang.get("select_resident_first"), parent=self)
            return
        if not messagebox.askyesno(
            lang.get("confirm_delete"),
            lang.get("confirm_remove_res", name=res.full_name),
            parent=self,
        ):
            return
        db.delete_resident(res.id)
        self._refresh_residents()
        self._refresh_events()
        self._on_change()
