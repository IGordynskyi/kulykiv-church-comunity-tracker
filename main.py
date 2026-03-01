import sys
import os
import tkinter as tk
from tkinter import ttk, messagebox, filedialog

if getattr(sys, "frozen", False):
    sys.path.insert(0, sys._MEIPASS)
else:
    sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import lang
import database as db
from ui.address_list import AddressListPanel
from ui.resident_view import ResidentViewPanel
from ui.dialogs import LanguageDialog
import export as exp


class MainWindow(tk.Tk):
    def __init__(self):
        super().__init__()

        db.init_db()

        # Load saved language before building any UI
        saved_lang = db.get_config("language", "en")
        lang.set_lang(saved_lang)

        self._set_icon()
        self.geometry("1050x660")
        self.minsize(780, 520)
        self._update_title()
        self._build_menu()
        self._build_ui()

    def _set_icon(self):
        """Set window / taskbar icon from img/church.png (and .ico on Windows)."""
        base = getattr(sys, "_MEIPASS", os.path.dirname(os.path.abspath(__file__)))
        # Windows taskbar / title bar: prefer .ico when available
        if sys.platform == "win32":
            ico = os.path.join(base, "img", "church.ico")
            if os.path.exists(ico):
                try:
                    self.iconbitmap(default=ico)
                    return
                except Exception:
                    pass
        # Linux / macOS / Windows fallback: PNG via iconphoto
        png = os.path.join(base, "img", "church.png")
        if os.path.exists(png):
            try:
                img = tk.PhotoImage(file=png)
                self.iconphoto(True, img)
                self._icon_img = img  # keep reference so GC doesn't destroy it
            except Exception:
                pass

    def _update_title(self):
        self.title(f"{lang.get('app_title')} — {lang.get('city_name')}")

    def _build_menu(self):
        self._menubar = tk.Menu(self)

        file_menu = tk.Menu(self._menubar, tearoff=0)
        file_menu.add_command(label=lang.get("menu_export_csv"),   command=self._export_csv)
        file_menu.add_command(label=lang.get("menu_export_excel"), command=self._export_excel)
        file_menu.add_separator()
        file_menu.add_command(label=lang.get("menu_import_csv"),   command=self._import_csv)
        file_menu.add_command(label=lang.get("menu_import_excel"), command=self._import_excel)
        file_menu.add_separator()
        file_menu.add_command(label=lang.get("menu_exit"), command=self.quit)
        self._menubar.add_cascade(label=lang.get("menu_file"), menu=file_menu)

        settings_menu = tk.Menu(self._menubar, tearoff=0)
        settings_menu.add_command(label=lang.get("menu_language"), command=self._change_language)
        self._menubar.add_cascade(label=lang.get("menu_settings"), menu=settings_menu)

        help_menu = tk.Menu(self._menubar, tearoff=0)
        help_menu.add_command(label=lang.get("menu_about"), command=self._show_about)
        self._menubar.add_cascade(label=lang.get("menu_help"), menu=help_menu)

        self.config(menu=self._menubar)

    def _build_ui(self):
        paned = tk.PanedWindow(self, orient="horizontal",
                               sashrelief="raised", sashwidth=5)
        paned.pack(fill="both", expand=True, padx=6, pady=6)

        self._addr_panel = AddressListPanel(paned, on_select=self._on_address_selected)
        self._res_panel  = ResidentViewPanel(paned, on_change=self._addr_panel.refresh)

        paned.add(self._addr_panel, minsize=230)
        paned.add(self._res_panel,  minsize=400)

        self.after(100, lambda: paned.sash_place(0, 270, 0))

        self._status_var = tk.StringVar(value=lang.get("ready"))
        ttk.Label(
            self, textvariable=self._status_var,
            relief="sunken", anchor="w", padding=(6, 2)
        ).pack(side="bottom", fill="x")

    def _on_address_selected(self, address):
        self._res_panel.load_address(address)
        if address:
            self._status_var.set(lang.get("status_viewing",
                                          street=address.street,
                                          count=address.active_count))
        else:
            self._status_var.set(lang.get("ready"))

    # ── Export ───────────────────────────────────────────────────────────────

    def _export_csv(self):
        backup_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "backup")
        os.makedirs(backup_dir, exist_ok=True)
        import datetime
        default_name = datetime.datetime.now().strftime("backup_%Y-%m-%d_%H-%M-%S.csv")
        path = filedialog.asksaveasfilename(
            defaultextension=".csv",
            filetypes=[("CSV files", "*.csv"), ("All files", "*.*")],
            title=lang.get("menu_export_csv").rstrip("…"),
            initialdir=backup_dir,
            initialfile=default_name,
        )
        if not path:
            return
        try:
            residents = db.get_all_residents()
            exp.export_csv(path, residents)
            self._status_var.set(lang.get("status_exported",
                                          count=len(residents),
                                          file=os.path.basename(path)))
        except Exception as e:
            messagebox.showerror(lang.get("export_failed"), str(e), parent=self)

    def _export_excel(self):
        reports_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "xlsx-reports")
        os.makedirs(reports_dir, exist_ok=True)
        import datetime
        default_name = datetime.datetime.now().strftime("export_%Y-%m-%d_%H-%M-%S.xlsx")
        path = filedialog.asksaveasfilename(
            defaultextension=".xlsx",
            filetypes=[("Excel files", "*.xlsx"), ("All files", "*.*")],
            title=lang.get("menu_export_excel").rstrip("…"),
            initialdir=reports_dir,
            initialfile=default_name,
        )
        if not path:
            return
        try:
            residents = db.get_all_residents()
            exp.export_excel(path, residents)
            self._status_var.set(lang.get("status_exported",
                                          count=len(residents),
                                          file=os.path.basename(path)))
        except Exception as e:
            messagebox.showerror(lang.get("export_failed"), str(e), parent=self)

    def _import_csv(self):
        path = filedialog.askopenfilename(
            filetypes=[("CSV files", "*.csv"), ("All files", "*.*")],
            title=lang.get("menu_import_csv").rstrip("…"),
        )
        if not path:
            return
        try:
            new, skip = exp.import_csv(path)
            self._addr_panel.refresh()
            self._status_var.set(lang.get("import_success",
                                          new=new, skip=skip,
                                          file=os.path.basename(path)))
        except Exception as e:
            messagebox.showerror(lang.get("import_failed"), str(e), parent=self)

    def _import_excel(self):
        path = filedialog.askopenfilename(
            filetypes=[("Excel files", "*.xlsx"), ("All files", "*.*")],
            title=lang.get("menu_import_excel").rstrip("…"),
        )
        if not path:
            return
        try:
            new, skip = exp.import_excel(path)
            self._addr_panel.refresh()
            self._status_var.set(lang.get("import_success",
                                          new=new, skip=skip,
                                          file=os.path.basename(path)))
        except Exception as e:
            messagebox.showerror(lang.get("import_failed"), str(e), parent=self)

    # ── Settings ─────────────────────────────────────────────────────────────

    def _change_language(self):
        dlg = LanguageDialog(self, lang.current())
        if dlg.result:
            db.set_config("language", dlg.result)
            messagebox.showinfo(
                lang.get("menu_language"),
                lang.get("lang_restart_note"),
                parent=self,
            )

    # ── Help ─────────────────────────────────────────────────────────────────

    def _show_about(self):
        messagebox.showinfo(lang.get("about_title"), lang.get("about_text"), parent=self)


if __name__ == "__main__":
    app = MainWindow()
    app.mainloop()
