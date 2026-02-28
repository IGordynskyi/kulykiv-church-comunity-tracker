import tkinter as tk
from tkinter import ttk, messagebox
from typing import Callable, Optional, List
from models import Address
import database as db
import lang
from ui.dialogs import AddressDialog


class AddressListPanel(ttk.Frame):
    """Left panel: scrollable list of addresses with resident counts."""

    def __init__(self, parent, on_select: Callable[[Optional[Address]], None]):
        super().__init__(parent)
        self._on_select = on_select
        self._addresses: List[Address] = []
        self._selected_id: Optional[int] = None

        self._build_ui()
        self.refresh()

    def _build_ui(self):
        ttk.Label(self, text=lang.get("addresses_header"),
                  font=("", 10, "bold")).pack(fill="x", padx=8, pady=(8, 4))

        list_frame = ttk.Frame(self)
        list_frame.pack(fill="both", expand=True, padx=4)

        scrollbar = ttk.Scrollbar(list_frame, orient="vertical")
        self._listbox = tk.Listbox(
            list_frame,
            yscrollcommand=scrollbar.set,
            selectmode="single",
            activestyle="dotbox",
            font=("", 10),
            relief="flat",
            borderwidth=0,
            highlightthickness=1,
        )
        scrollbar.config(command=self._listbox.yview)
        scrollbar.pack(side="right", fill="y")
        self._listbox.pack(side="left", fill="both", expand=True)
        self._listbox.bind("<<ListboxSelect>>", self._on_listbox_select)
        self._listbox.bind("<Double-Button-1>", lambda e: self._edit_address())

        btn_frame = ttk.Frame(self)
        btn_frame.pack(fill="x", padx=8, pady=8)
        ttk.Button(btn_frame, text=lang.get("btn_add"),    command=self._add_address).pack(side="left", padx=2)
        ttk.Button(btn_frame, text=lang.get("btn_edit"),   command=self._edit_address).pack(side="left", padx=2)
        ttk.Button(btn_frame, text=lang.get("btn_delete"), command=self._delete_address).pack(side="left", padx=2)

        ttk.Separator(self, orient="horizontal").pack(fill="x", padx=8)
        self._total_var = tk.StringVar()
        ttk.Label(self, textvariable=self._total_var,
                  font=("", 9, "bold"), anchor="center").pack(fill="x", padx=8, pady=(4, 8))

    def refresh(self):
        self._addresses = db.get_addresses()
        self._listbox.delete(0, "end")
        for addr in self._addresses:
            self._listbox.insert("end", f"  {addr.street}  ({addr.active_count})")

        total = sum(a.active_count for a in self._addresses)
        self._total_var.set(lang.get("lbl_active_total", count=total))

        if self._selected_id is not None:
            for i, a in enumerate(self._addresses):
                if a.id == self._selected_id:
                    self._listbox.selection_set(i)
                    self._listbox.see(i)
                    break
            else:
                self._selected_id = None
                self._on_select(None)

    def _on_listbox_select(self, _event=None):
        sel = self._listbox.curselection()
        if sel:
            self._selected_id = self._addresses[sel[0]].id
            self._on_select(self._addresses[sel[0]])
        else:
            self._selected_id = None
            self._on_select(None)

    def _selected_address(self) -> Optional[Address]:
        sel = self._listbox.curselection()
        return self._addresses[sel[0]] if sel else None

    def _add_address(self):
        dlg = AddressDialog(self)
        if dlg.result:
            db.add_address(dlg.result.street, dlg.result.notes)
            self.refresh()

    def _edit_address(self):
        addr = self._selected_address()
        if not addr:
            messagebox.showinfo(lang.get("info"),
                                lang.get("select_address_first"), parent=self)
            return
        dlg = AddressDialog(self, addr)
        if dlg.result:
            db.update_address(dlg.result)
            self.refresh()

    def _delete_address(self):
        addr = self._selected_address()
        if not addr:
            messagebox.showinfo(lang.get("info"),
                                lang.get("select_address_first"), parent=self)
            return
        if not messagebox.askyesno(
            lang.get("confirm_delete"),
            lang.get("confirm_delete_addr", street=addr.street),
            parent=self,
        ):
            return
        db.delete_address(addr.id)
        self._selected_id = None
        self._on_select(None)
        self.refresh()
