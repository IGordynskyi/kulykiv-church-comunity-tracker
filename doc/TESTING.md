# Testing Guide

## Prerequisites

Install `pytest` if not already available:

```bash
pip3 install pytest
```

The only other dependency used by the app itself is `openpyxl` (for Excel export/import), listed in `requirements.txt`:

```bash
pip3 install -r requirements.txt
```

## Running the Tests

Run all tests from the project root:

```bash
python3 -m pytest tests/ -v
```

Run a single test file:

```bash
python3 -m pytest tests/test_database.py -v
```

Run a single test class or test:

```bash
python3 -m pytest tests/test_database.py::TestResidents -v
python3 -m pytest tests/test_database.py::TestResidents::test_mark_deceased -v
```

Run with a short summary (no verbose output):

```bash
python3 -m pytest tests/
```

> **Note:** Tests never touch the real `church.db`. Each database test gets its own temporary SQLite file that is deleted automatically after the test.

---

## Test Files and Coverage

### `tests/test_models.py` — Data model classes

| Test | Description |
|---|---|
| `TestAddress::test_basic_creation` | Address is created with correct id, street, and default empty notes/count |
| `TestAddress::test_with_all_fields` | Address stores notes and active_count when provided |
| `TestAddress::test_id_can_be_none` | Address id accepts `None` (before DB insertion) |
| `TestResident::test_full_name` | `full_name` property concatenates first and last name |
| `TestResident::test_is_baptized_true` | `is_baptized` is `True` when `baptism_date` is set |
| `TestResident::test_is_baptized_false` | `is_baptized` is `False` when `baptism_date` is `None` |
| `TestResident::test_is_married_via_date` | `is_married` is `True` when `marriage_date` is set |
| `TestResident::test_is_married_via_spouse` | `is_married` is `True` when `spouse` name is set |
| `TestResident::test_is_married_neither` | `is_married` is `False` when both date and spouse are absent |
| `TestResident::test_is_married_empty_spouse` | Empty string spouse does not count as married |
| `TestResident::test_default_status` | Default status is `"active"` |
| `TestResident::test_all_optional_fields_default_none` | All date and family fields default to `None` |
| `TestResident::test_notes_default_empty` | Notes field defaults to empty string |
| `TestEvent::test_basic_creation` | Event stores type, date, and defaults description/names to empty |
| `TestEvent::test_with_all_fields` | Event stores description and resident_name when provided |
| `TestEvent::test_id_can_be_none` | Event id accepts `None` (before DB insertion) |

---

### `tests/test_lang.py` — Internationalisation (i18n)

| Test | Description |
|---|---|
| `TestSetLang::test_set_english` | Setting language to `"en"` is reflected by `current()` |
| `TestSetLang::test_set_ukrainian` | Setting language to `"uk"` is reflected by `current()` |
| `TestSetLang::test_invalid_lang_ignored` | Unsupported language code leaves the current language unchanged |
| `TestSetLang::test_empty_string_ignored` | Empty string is rejected as a language code |
| `TestGet::test_known_key_english` | Returns correct English string for a known key |
| `TestGet::test_known_key_ukrainian` | Returns correct Ukrainian string for a known key |
| `TestGet::test_missing_key_returns_bracket_form` | Unknown key returns `[key]` placeholder |
| `TestGet::test_format_substitution` | Named kwargs are substituted into the template string (English) |
| `TestGet::test_format_substitution_ukrainian` | Named kwargs are substituted into the template string (Ukrainian) |
| `TestGet::test_no_kwargs_returns_plain_string` | Keys without placeholders return the string unchanged |
| `TestGet::test_about_text_multiline` | About text is a multi-line string containing "Version" |
| `TestGet::test_app_title_english` | App title is non-empty in English |
| `TestGet::test_app_title_ukrainian_differs_from_english` | App title differs between English and Ukrainian |
| `TestEventTypes::test_returns_four_items_en` | `event_types()` returns exactly 4 items in English |
| `TestEventTypes::test_returns_four_items_uk` | `event_types()` returns exactly 4 items in Ukrainian |
| `TestEventTypes::test_english_event_types` | English event type labels are correct |
| `TestEventTypes::test_ukrainian_event_types` | Ukrainian event type labels are correct |
| `TestEventTypeToKey::test_english_localized_to_key` | English labels convert back to bare DB keys |
| `TestEventTypeToKey::test_ukrainian_localized_to_key` | Ukrainian labels convert back to bare DB keys |
| `TestEventTypeToKey::test_bare_english_key_passthrough` | Bare EN keys stored in DB are returned as-is |
| `TestEventTypeToKey::test_unknown_returns_itself` | Unrecognised string passes through unchanged |
| `TestEventKeyToLabel::test_english_labels` | DB keys map to correct English display labels |
| `TestEventKeyToLabel::test_ukrainian_labels` | DB keys map to correct Ukrainian display labels |
| `TestEventKeyToLabel::test_unknown_key_passthrough` | Unknown DB key passes through unchanged |

---

### `tests/test_database.py` — Database layer

| Test | Description |
|---|---|
| `TestConfig::test_get_missing_key_returns_default` | `get_config` returns the given default for absent keys |
| `TestConfig::test_get_missing_key_empty_default` | `get_config` returns `""` when no default is supplied |
| `TestConfig::test_set_and_get` | A value written with `set_config` is readable back with `get_config` |
| `TestConfig::test_set_overwrites` | Calling `set_config` twice on the same key updates the value |
| `TestAddressSortKey::test_numbered_street` | Street with trailing number sorts as `(name, number)` |
| `TestAddressSortKey::test_numbered_street_casefold` | Sort key is case-folded for case-insensitive ordering |
| `TestAddressSortKey::test_no_number` | Street without a number uses `0` as the building number |
| `TestAddressSortKey::test_cyrillic_street` | Cyrillic street names with numbers are parsed correctly |
| `TestAddressSortKey::test_strips_whitespace` | Leading/trailing whitespace is ignored in the sort key |
| `TestAddresses::test_add_address_returns_address` | `add_address` returns an `Address` with an assigned id |
| `TestAddresses::test_add_address_with_notes` | Notes are stored when passed to `add_address` |
| `TestAddresses::test_get_addresses_empty` | `get_addresses` returns an empty list when no addresses exist |
| `TestAddresses::test_get_addresses_returns_all` | All added addresses are returned |
| `TestAddresses::test_get_addresses_sorted_naturally` | Addresses are sorted with natural number ordering (`Oak Ave 2` before `Oak Ave 10`) |
| `TestAddresses::test_get_addresses_active_count` | `active_count` reflects the number of active residents at that address |
| `TestAddresses::test_update_address` | `update_address` persists changes to street and notes |
| `TestAddresses::test_delete_address` | `delete_address` removes the address from the database |
| `TestAddresses::test_delete_address_cascades_to_residents` | Deleting an address also deletes its residents |
| `TestAddresses::test_find_or_create_address_creates_new` | `find_or_create_address` inserts a new address when none matches |
| `TestAddresses::test_find_or_create_address_finds_existing` | `find_or_create_address` is case-insensitive and reuses existing addresses |
| `TestAddresses::test_find_or_create_strips_whitespace` | Surrounding whitespace in the street name is ignored when matching |
| `TestResidentExists::test_returns_false_when_absent` | Returns `False` when no matching resident exists |
| `TestResidentExists::test_returns_true_when_present` | Returns `True` for an existing resident |
| `TestResidentExists::test_case_insensitive` | Name matching is case-insensitive |
| `TestResidentExists::test_different_address_returns_false` | Same name at a different address returns `False` |
| `TestResidents::test_add_resident_assigns_id` | `add_resident` sets the `id` field on the returned object |
| `TestResidents::test_get_residents_returns_for_address` | `get_residents` returns only residents at the given address |
| `TestResidents::test_get_residents_empty_for_unknown_address` | Returns empty list for an address with no residents |
| `TestResidents::test_get_residents_sorted_by_name` | Residents are sorted alphabetically by last name then first name |
| `TestResidents::test_get_all_residents` | `get_all_residents` returns residents from all addresses |
| `TestResidents::test_update_resident` | `update_resident` persists name and status changes |
| `TestResidents::test_delete_resident` | `delete_resident` removes the resident from the database |
| `TestResidents::test_mark_deceased` | `mark_deceased` sets status to `"deceased"` and stores the death date |
| `TestResidents::test_mark_left` | `mark_left` sets status to `"left"` |
| `TestResidents::test_active_count_excludes_deceased` | Deceased residents are not counted as active |
| `TestResidents::test_active_count_excludes_left` | Residents who have left are not counted as active |
| `TestResidents::test_resident_all_fields_roundtrip` | All optional fields (dates, family names, notes) survive a DB round-trip |
| `TestEvents::test_add_event_assigns_id` | `add_event` sets the `id` field on the returned object |
| `TestEvents::test_get_events_for_address` | Events for residents of an address are returned correctly |
| `TestEvents::test_get_events_includes_resident_name` | Returned events include the full name of the linked resident |
| `TestEvents::test_get_events_sorted_by_date_desc` | Events are returned in reverse chronological order |
| `TestEvents::test_get_events_empty_for_unknown_address` | Returns empty list when the address has no events |
| `TestEvents::test_delete_resident_cascades_to_events` | Deleting a resident also deletes their events |

---

### `tests/test_export.py` — Export and import

| Test | Description |
|---|---|
| `TestCellHelper::test_returns_value_at_index` | `_cell` returns the value at the specified column index |
| `TestCellHelper::test_strips_whitespace` | `_cell` strips leading/trailing whitespace from values |
| `TestCellHelper::test_out_of_bounds_returns_default` | `_cell` returns `""` when the index is beyond the row length |
| `TestCellHelper::test_out_of_bounds_custom_default` | `_cell` returns the custom default when the index is out of bounds |
| `TestCellHelper::test_converts_non_string` | `_cell` converts non-string values (e.g. integers) to strings |
| `TestDateOrNone::test_returns_value_when_present` | `_date_or_none` returns the date string when non-empty |
| `TestDateOrNone::test_returns_none_for_empty_string` | `_date_or_none` returns `None` for an empty cell |
| `TestDateOrNone::test_returns_none_out_of_bounds` | `_date_or_none` returns `None` when the index is out of bounds |
| `TestResidentRow::test_active_status_label` | Active residents get the English "active" label in the export row |
| `TestResidentRow::test_deceased_status_label` | Deceased residents get the English "deceased" label |
| `TestResidentRow::test_left_status_label` | Residents who left get the English "left" label |
| `TestResidentRow::test_ukrainian_status_deceased` | Status label is localised to Ukrainian when Ukrainian is active |
| `TestResidentRow::test_date_fields_empty_when_none` | Date columns are empty strings when the resident has no dates |
| `TestResidentRow::test_date_fields_populated` | Date columns contain the stored date strings when present |
| `TestResidentRow::test_name_fields` | Last name is column 0, first name is column 1 in the export row |
| `TestExportCsv::test_header_row_present` | Exported CSV contains a header row with column names |
| `TestExportCsv::test_data_row_count` | Exported CSV contains one data row per resident plus the header |
| `TestExportCsv::test_data_sorted_by_last_then_first` | Residents are sorted by last name then first name in the export |
| `TestExportCsv::test_clears_address_cache_before_export` | The address lookup cache is cleared at the start of each export |
| `TestImportRows::test_skips_empty_rows` | Importing an empty list produces zero new and zero skipped records |
| `TestImportRows::test_skips_rows_with_missing_fields` | Rows missing last name, first name, or street are silently skipped |
| `TestImportRows::test_imports_new_resident` | A valid row creates a new resident and increments the new counter |
| `TestImportRows::test_skips_duplicate_resident` | Re-importing the same row increments the skip counter instead |
| `TestImportRows::test_status_mapping_ukrainian` | Ukrainian status label `"активний"` maps to DB value `"active"` |
| `TestImportRows::test_status_mapping_deceased` | Status label `"deceased"` maps to DB value `"deceased"` |
| `TestImportRows::test_unknown_status_defaults_to_active` | Unrecognised status values default to `"active"` |
| `TestCsvRoundTrip::test_export_then_import` | A resident exported to CSV and re-imported into a fresh DB retains all field values |
| `TestExportExcel::test_creates_xlsx_file` | `export_excel` creates a real `.xlsx` file on disk |
| `TestExportExcel::test_header_row_present` | Exported `.xlsx` contains a header row with column names |
| `TestExportExcel::test_header_is_bold` | Header row cells are formatted bold in the Excel output |
| `TestExportExcel::test_data_row_count` | Exported `.xlsx` contains one data row per resident plus the header |
| `TestExportExcel::test_empty_residents_only_header` | Exporting an empty list produces a file with only the header row |
| `TestExportExcel::test_data_sorted_by_last_then_first` | Residents are sorted by last name then first name in the Excel export |
| `TestExportExcel::test_date_fields_written` | Date columns are written correctly; absent dates produce an empty/null cell |
| `TestExportExcel::test_clears_address_cache_before_export` | The address lookup cache is cleared at the start of each Excel export |
| `TestExportExcel::test_raises_runtime_error_without_openpyxl` | `export_excel` raises `RuntimeError` with an install hint when `openpyxl` is missing |
| `TestImportExcel::test_raises_runtime_error_without_openpyxl` | `import_excel` raises `RuntimeError` with an install hint when `openpyxl` is missing |
| `TestImportExcel::test_skips_header_row` | The header row of the `.xlsx` file is not imported as a resident record |
| `TestImportExcel::test_imports_new_resident` | A valid row in an `.xlsx` file creates a new resident with all fields |
| `TestImportExcel::test_skips_duplicate_resident` | Re-importing the same `.xlsx` row increments the skip counter instead |
| `TestImportExcel::test_date_fields_imported` | Birth, baptism, and death dates are read correctly from Excel cells |
| `TestImportExcel::test_status_mapping_ukrainian` | Ukrainian status label `"активний"` in Excel maps to DB value `"active"` |
| `TestImportExcel::test_status_mapping_deceased` | Status label `"deceased"` in Excel maps to DB value `"deceased"` |
| `TestImportExcel::test_status_mapping_left_ukrainian` | Ukrainian status label `"виїхав"` in Excel maps to DB value `"left"` |
| `TestImportExcel::test_unknown_status_defaults_to_active` | Unrecognised status values in Excel default to `"active"` |
| `TestImportExcel::test_skips_rows_with_missing_fields` | Excel rows missing last name, first name, or street are silently skipped |
| `TestExcelRoundTrip::test_export_then_import` | A resident exported to `.xlsx` and re-imported into a fresh DB retains all field values |
