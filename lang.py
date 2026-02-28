"""
Language / i18n module.
All UI strings are defined here in English and Ukrainian.
Call lang.get('key') anywhere in the app.
"""

_STRINGS = {
    # ── General ──────────────────────────────────────────────────────────────
    "app_title":            {"en": "Parafiya Tserkvy Uspinnya Presvyatoyi Bohorodytsi",
                             "uk": "Парафія Церкви Успіння Пресвятої Богородиці"},
    "city_name":            {"en": "Kulykiv",            "uk": "Куликів"},
    "ready":                {"en": "Ready",              "uk": "Готово"},
    "save":                 {"en": "Save",               "uk": "Зберегти"},
    "cancel":               {"en": "Cancel",             "uk": "Скасувати"},
    "confirm":              {"en": "Confirm",            "uk": "Підтвердити"},
    "yes":                  {"en": "yes",                "uk": "так"},
    "no":                   {"en": "no",                 "uk": "ні"},
    "error":                {"en": "Error",              "uk": "Помилка"},
    "info":                 {"en": "Info",               "uk": "Інформація"},
    "date_hint":            {"en": "DD.MM.YYYY",         "uk": "ДД.ММ.РРРР"},

    # ── Menu ─────────────────────────────────────────────────────────────────
    "menu_file":            {"en": "File",               "uk": "Файл"},
    "menu_settings":        {"en": "Settings",           "uk": "Налаштування"},
    "menu_help":            {"en": "Help",               "uk": "Допомога"},
    "menu_export_csv":      {"en": "Export to CSV…",     "uk": "Експорт у CSV…"},
    "menu_export_excel":    {"en": "Export to Excel…",   "uk": "Експорт у Excel…"},
    "menu_import_csv":      {"en": "Import from CSV…",   "uk": "Імпорт з CSV…"},
    "menu_import_excel":    {"en": "Import from Excel…", "uk": "Імпорт з Excel…"},
    "menu_exit":            {"en": "Exit",               "uk": "Вийти"},
    "menu_city":            {"en": "Change City Name…",  "uk": "Змінити назву міста…"},
    "menu_language":        {"en": "Language / Мова…",   "uk": "Language / Мова…"},
    "menu_about":           {"en": "About",              "uk": "Про програму"},

    # ── Status bar ───────────────────────────────────────────────────────────
    "status_viewing":       {"en": "Viewing: {street}  •  {count} active resident(s)",
                             "uk": "Перегляд: {street}  •  {count} активних мешканців"},
    "status_exported":      {"en": "Exported {count} residents to {file}",
                             "uk": "Експортовано {count} мешканців у {file}"},

    # ── Address panel ────────────────────────────────────────────────────────
    "addresses_header":     {"en": "ADDRESSES",          "uk": "АДРЕСИ"},
    "lbl_active_total":     {"en": "Parishioners: {count}",
                             "uk": "Парафіян: {count}"},
    "btn_add":              {"en": "+ Add",              "uk": "+ Додати"},
    "btn_edit":             {"en": "Edit",               "uk": "Правити"},
    "btn_delete":           {"en": "Delete",             "uk": "Видалити"},
    "select_address_first": {"en": "Please select an address first.",
                             "uk": "Будь ласка, оберіть адресу."},
    "confirm_delete_addr":  {"en": "Delete '{street}' and ALL its residents?\nThis cannot be undone.",
                             "uk": "Видалити '{street}' та ВСІХ її мешканців?\nЦю дію не можна скасувати."},
    "confirm_delete":       {"en": "Confirm Delete",     "uk": "Підтвердити видалення"},

    # ── Address dialog ───────────────────────────────────────────────────────
    "dlg_add_address":      {"en": "Add Address",        "uk": "Додати адресу"},
    "dlg_edit_address":     {"en": "Edit Address",       "uk": "Редагувати адресу"},
    "lbl_street":           {"en": "Street address:",    "uk": "Вулиця та номер будинку:"},
    "lbl_street_hint":      {"en": "e.g. Church Lane 12  or  Шевченка 5",
                             "uk": "напр. Church Lane 12  або  Шевченка 5"},
    "lbl_notes":            {"en": "Notes:",             "uk": "Примітки:"},
    "err_street_required":  {"en": "Street address is required.",
                             "uk": "Адреса вулиці обов'язкова."},

    # ── Resident panel ───────────────────────────────────────────────────────
    "select_address_placeholder": {"en": "← Select an address",
                                   "uk": "← Оберіть адресу"},
    "col_name":             {"en": "Name",               "uk": "Ім'я"},
    "col_dob":              {"en": "Date of Birth",      "uk": "Дата народження"},
    "col_baptized":         {"en": "Baptized",           "uk": "Охрещений"},
    "col_married":          {"en": "Married",            "uk": "Одружений"},
    "col_status":           {"en": "Status",             "uk": "Статус"},
    "col_dod":              {"en": "Date of Death",      "uk": "Дата смерті"},
    "status_active":        {"en": "active",             "uk": "активний"},
    "status_deceased":      {"en": "deceased",           "uk": "помер"},
    "status_left":          {"en": "left",               "uk": "виїхав"},
    "btn_add_member":       {"en": "+ Add Member",       "uk": "+ Додати члена"},
    "btn_view":             {"en": "View",               "uk": "Перегляд"},
    "btn_record_event":     {"en": "Record Event",       "uk": "Записати подію"},
    "btn_mark_deceased":    {"en": "Mark Deceased",      "uk": "Відмітити померлим"},
    "btn_mark_left":        {"en": "Mark Left",          "uk": "Виїхав"},
    "btn_remove":           {"en": "Remove",             "uk": "Видалити"},
    "event_history":        {"en": "Event History",      "uk": "Історія подій"},
    "no_events":            {"en": "No events recorded yet.",
                             "uk": "Подій ще не записано."},
    "select_resident_first":{"en": "Please select a resident first.",
                             "uk": "Будь ласка, оберіть мешканця."},
    "already_deceased":     {"en": "Already Deceased",  "uk": "Вже відмічений померлим"},
    "already_deceased_msg": {"en": "{name} is already marked as deceased.",
                             "uk": "{name} вже відмічений як померлий."},
    "already_left":         {"en": "Already Left",      "uk": "Вже виїхав"},
    "already_left_msg":     {"en": "{name} is already marked as left.",
                             "uk": "{name} вже відмічений як виїхавший."},
    "confirm_mark_left":    {"en": "Mark {name} as having left the community?",
                             "uk": "Відмітити {name} як виїхавшого з громади?"},
    "confirm_remove_res":   {"en": "Remove {name} from this address?\nAll their events will also be deleted.",
                             "uk": "Видалити {name} з цієї адреси?\nУсі їхні події також будуть видалені."},

    # ── Resident dialog ──────────────────────────────────────────────────────
    "dlg_add_resident":     {"en": "Add Resident",       "uk": "Додати мешканця"},
    "dlg_edit_resident":    {"en": "Edit Resident",      "uk": "Редагувати мешканця"},
    "lbl_first_name":       {"en": "First name:",        "uk": "Ім'я:"},
    "lbl_last_name":        {"en": "Last name:",         "uk": "Прізвище:"},
    "lbl_father":           {"en": "Father:",            "uk": "Батько:"},
    "lbl_mother":           {"en": "Mother:",            "uk": "Мати:"},
    "lbl_spouse":           {"en": "Husband / Wife:",    "uk": "Чоловік / Дружина:"},
    "lbl_dob":              {"en": "Date of birth:",     "uk": "Дата народження:"},
    "lbl_baptism":          {"en": "Date of baptism:",   "uk": "Дата хрещення:"},
    "lbl_marriage":         {"en": "Date of marriage:",  "uk": "Дата вінчання:"},
    "lbl_death":            {"en": "Date of death:",     "uk": "Дата смерті:"},
    "err_name_required":    {"en": "First and last name are required.",
                             "uk": "Ім'я та прізвище обов'язкові."},
    "err_invalid_date":     {"en": "Invalid date",       "uk": "Невірна дата"},
    "err_date_format":      {"en": "{field} must be in DD.MM.YYYY format.",
                             "uk": "{field} має бути у форматі ДД.ММ.РРРР."},

    # ── Mark deceased dialog ─────────────────────────────────────────────────
    "dlg_mark_deceased":    {"en": "Mark Deceased — {name}",
                             "uk": "Відмітити померлим — {name}"},
    "lbl_recording_death":  {"en": "Recording death for: {name}",
                             "uk": "Записуємо дату смерті для: {name}"},
    "err_death_date_required": {"en": "Please enter the date of death.",
                                "uk": "Будь ласка, введіть дату смерті."},

    # ── Event dialog ─────────────────────────────────────────────────────────
    "dlg_record_event":     {"en": "Record Event — {name}",
                             "uk": "Записати подію — {name}"},
    "lbl_resident":         {"en": "Resident: {name}",  "uk": "Мешканець: {name}"},
    "lbl_event_type":       {"en": "Event type:",       "uk": "Тип події:"},
    "lbl_event_date":       {"en": "Event date:",       "uk": "Дата події:"},
    "lbl_description":      {"en": "Description:",      "uk": "Опис:"},
    "err_event_date_required": {"en": "Event date is required.",
                                "uk": "Дата події обов'язкова."},
    "event_birth":          {"en": "birth",             "uk": "народження"},
    "event_baptism":        {"en": "baptism",           "uk": "хрещення"},
    "event_marriage":       {"en": "marriage",          "uk": "шлюб"},
    "event_death":          {"en": "death",             "uk": "смерть"},

    # ── Auto-generated event descriptions ────────────────────────────────────
    "auto_born":            {"en": "{name} was born",
                             "uk": "{name} народився/лась"},
    "auto_died":            {"en": "{name} passed away",
                             "uk": "{name} помер/ла"},

    # ── City dialog ──────────────────────────────────────────────────────────
    "dlg_city":             {"en": "Set City Name",     "uk": "Вказати назву міста"},
    "lbl_city":             {"en": "City name:",        "uk": "Назва міста:"},
    "err_city_required":    {"en": "City name is required.",
                             "uk": "Назва міста обов'язкова."},

    # ── Language dialog ──────────────────────────────────────────────────────
    "dlg_language":         {"en": "Select Language",   "uk": "Оберіть мову"},
    "lang_restart_note":    {"en": "Language will change after you restart the app.",
                             "uk": "Мова зміниться після перезапуску програми."},

    # ── Export ───────────────────────────────────────────────────────────────
    "export_col_last":      {"en": "Last Name",         "uk": "Прізвище"},
    "export_col_first":     {"en": "First Name",        "uk": "Ім'я"},
    "export_col_address":   {"en": "Address",           "uk": "Адреса"},
    "export_col_status":    {"en": "Status",            "uk": "Статус"},
    "export_col_dob":       {"en": "Date of Birth",     "uk": "Дата народження"},
    "export_col_baptism":   {"en": "Date of Baptism",   "uk": "Дата хрещення"},
    "export_col_marriage":  {"en": "Date of Marriage",  "uk": "Дата вінчання"},
    "export_col_death":     {"en": "Date of Death",     "uk": "Дата смерті"},
    "export_col_notes":     {"en": "Notes",             "uk": "Примітки"},
    "export_failed":        {"en": "Export failed",     "uk": "Помилка експорту"},
    "import_success":       {"en": "Imported {new} resident(s) from {file}, skipped {skip} duplicate(s).",
                             "uk": "Імпортовано {new} ос. з {file}, пропущено {skip} дублів."},
    "import_failed":        {"en": "Import failed",     "uk": "Помилка імпорту"},

    # ── About ────────────────────────────────────────────────────────────────
    "about_title":          {"en": "About",             "uk": "Про програму"},
    "about_text":           {
        "en": (
            "Church Community Population Tracker\n"
            "Version 1.0\n\n"
            "Track residents, life events, and family groups\n"
            "for your church community.\n\n"
            "Data is stored locally in church.db"
        ),
        "uk": (
            "Трекер населення церковної громади\n"
            "Версія 1.0\n\n"
            "Відстежуйте мешканців, події та сімейні групи\n"
            "вашої церковної громади.\n\n"
            "Дані зберігаються локально у файлі church.db"
        ),
    },
}

# Current language — default English; overridden by main.py after DB config is read
_current: str = "en"

SUPPORTED = {"en": "English", "uk": "Українська"}


def set_lang(code: str):
    global _current
    if code in SUPPORTED:
        _current = code


def current() -> str:
    return _current


def get(key: str, **kwargs) -> str:
    """Return the translated string for key, with optional .format() kwargs."""
    entry = _STRINGS.get(key)
    if entry is None:
        return f"[{key}]"
    text = entry.get(_current, entry.get("en", f"[{key}]"))
    return text.format(**kwargs) if kwargs else text


def event_types() -> list:
    """Return the four event type strings in the current language."""
    return [get("event_birth"), get("event_baptism"),
            get("event_marriage"), get("event_death")]


def event_type_to_key(localized: str) -> str:
    """Convert a (possibly localized) event type back to the EN key stored in DB."""
    mapping = {get(k): k.replace("event_", "") for k in
               ("event_birth", "event_baptism", "event_marriage", "event_death")}
    # also accept bare EN keys already stored in DB
    for k in ("birth", "baptism", "marriage", "death"):
        mapping[k] = k
    return mapping.get(localized, localized)


def event_key_to_label(db_key: str) -> str:
    """Convert a DB event_type key ('birth', etc.) to the current-language label."""
    mapping = {
        "birth":    get("event_birth"),
        "baptism":  get("event_baptism"),
        "marriage": get("event_marriage"),
        "death":    get("event_death"),
    }
    return mapping.get(db_key, db_key)
