"""Tests for database.py — all CRUD operations against an isolated temp DB."""
import pytest
from unittest.mock import patch
from models import Address, Resident, Event


# ── Fixtures ──────────────────────────────────────────────────────────────────

@pytest.fixture
def db(tmp_path):
    """Fresh isolated database for each test."""
    db_file = str(tmp_path / "test.db")
    with patch("database.DB_PATH", db_file):
        import database as _db
        _db.init_db()
        yield _db


@pytest.fixture
def addr(db):
    """A pre-created address for reuse."""
    return db.add_address("Shevchenko 5", "near market")


@pytest.fixture
def resident(db, addr):
    """A pre-created resident linked to addr."""
    r = Resident(
        id=None, address_id=addr.id,
        first_name="Ivan", last_name="Kovalenko",
        birth_date="1980-04-10", status="active"
    )
    return db.add_resident(r)


# ── Config ────────────────────────────────────────────────────────────────────

class TestConfig:
    def test_get_missing_key_returns_default(self, db):
        assert db.get_config("no_such_key", "fallback") == "fallback"

    def test_get_missing_key_empty_default(self, db):
        assert db.get_config("no_such_key") == ""

    def test_set_and_get(self, db):
        db.set_config("language", "uk")
        assert db.get_config("language") == "uk"

    def test_set_overwrites(self, db):
        db.set_config("language", "en")
        db.set_config("language", "uk")
        assert db.get_config("language") == "uk"


# ── Address sort key ─────────────────────────────────────────────────────────

class TestAddressSortKey:
    def test_numbered_street(self, db):
        key = db._address_sort_key("Oak Lane 12")
        assert key == ("oak lane", 12)

    def test_numbered_street_casefold(self, db):
        key = db._address_sort_key("MAIN Street 3")
        assert key == ("main street", 3)

    def test_no_number(self, db):
        key = db._address_sort_key("Central")
        assert key == ("central", 0)

    def test_cyrillic_street(self, db):
        key = db._address_sort_key("вул. Незалежності 15")
        assert key == ("вул. незалежності", 15)

    def test_strips_whitespace(self, db):
        key = db._address_sort_key("  Oak Lane 7  ")
        assert key == ("oak lane", 7)


# ── Addresses ─────────────────────────────────────────────────────────────────

class TestAddresses:
    def test_add_address_returns_address(self, db):
        addr = db.add_address("Main St 1")
        assert addr.id is not None
        assert addr.street == "Main St 1"
        assert addr.notes == ""

    def test_add_address_with_notes(self, db):
        addr = db.add_address("Oak Ave 5", "corner house")
        assert addr.notes == "corner house"

    def test_get_addresses_empty(self, db):
        assert db.get_addresses() == []

    def test_get_addresses_returns_all(self, db):
        db.add_address("Elm St 1")
        db.add_address("Oak Ave 2")
        addresses = db.get_addresses()
        assert len(addresses) == 2

    def test_get_addresses_sorted_naturally(self, db):
        db.add_address("Oak Ave 10")
        db.add_address("Oak Ave 2")
        db.add_address("Ash Ln 1")
        streets = [a.street for a in db.get_addresses()]
        assert streets.index("Ash Ln 1") < streets.index("Oak Ave 2")
        assert streets.index("Oak Ave 2") < streets.index("Oak Ave 10")

    def test_get_addresses_active_count(self, db):
        addr = db.add_address("Pine Rd 3")
        r = Resident(id=None, address_id=addr.id, first_name="A", last_name="B")
        db.add_resident(r)
        addresses = db.get_addresses()
        assert addresses[0].active_count == 1

    def test_update_address(self, db, addr):
        addr.street = "New Street 99"
        addr.notes = "updated"
        db.update_address(addr)
        updated = db.get_addresses()[0]
        assert updated.street == "New Street 99"
        assert updated.notes == "updated"

    def test_delete_address(self, db):
        addr = db.add_address("Temp St 1")
        db.delete_address(addr.id)
        assert db.get_addresses() == []

    def test_delete_address_cascades_to_residents(self, db):
        addr = db.add_address("Cascade St 1")
        r = Resident(id=None, address_id=addr.id, first_name="X", last_name="Y")
        db.add_resident(r)
        db.delete_address(addr.id)
        assert db.get_all_residents() == []

    def test_find_or_create_address_creates_new(self, db):
        addr_id = db.find_or_create_address("Brand New St 7")
        assert addr_id is not None
        streets = [a.street for a in db.get_addresses()]
        assert "Brand New St 7" in streets

    def test_find_or_create_address_finds_existing(self, db):
        first_id = db.find_or_create_address("Repeat St 1")
        second_id = db.find_or_create_address("repeat st 1")  # case-insensitive
        assert first_id == second_id

    def test_find_or_create_strips_whitespace(self, db):
        id1 = db.find_or_create_address("Trim St 1")
        id2 = db.find_or_create_address("  Trim St 1  ")
        assert id1 == id2


# ── Resident existence check ──────────────────────────────────────────────────

class TestResidentExists:
    def test_returns_false_when_absent(self, db, addr):
        assert db.resident_exists(addr.id, "Nobody", "Here") is False

    def test_returns_true_when_present(self, db, addr, resident):
        assert db.resident_exists(addr.id, "Ivan", "Kovalenko") is True

    def test_case_insensitive(self, db, addr, resident):
        assert db.resident_exists(addr.id, "ivan", "kovalenko") is True

    def test_different_address_returns_false(self, db, addr, resident):
        addr2 = db.add_address("Other St 2")
        assert db.resident_exists(addr2.id, "Ivan", "Kovalenko") is False


# ── Residents ─────────────────────────────────────────────────────────────────

class TestResidents:
    def test_add_resident_assigns_id(self, db, addr):
        r = Resident(id=None, address_id=addr.id, first_name="Maria", last_name="Petrenko")
        added = db.add_resident(r)
        assert added.id is not None

    def test_get_residents_returns_for_address(self, db, addr, resident):
        residents = db.get_residents(addr.id)
        assert len(residents) == 1
        assert residents[0].first_name == "Ivan"

    def test_get_residents_empty_for_unknown_address(self, db):
        assert db.get_residents(9999) == []

    def test_get_residents_sorted_by_name(self, db, addr):
        db.add_resident(Resident(id=None, address_id=addr.id, first_name="Zoriana", last_name="Bila"))
        db.add_resident(Resident(id=None, address_id=addr.id, first_name="Anna", last_name="Bila"))
        names = [r.first_name for r in db.get_residents(addr.id)]
        assert names.index("Anna") < names.index("Zoriana")

    def test_get_all_residents(self, db, addr, resident):
        addr2 = db.add_address("Second St 2")
        db.add_resident(Resident(id=None, address_id=addr2.id, first_name="Oksana", last_name="Melnyk"))
        all_r = db.get_all_residents()
        assert len(all_r) == 2

    def test_update_resident(self, db, addr, resident):
        resident.first_name = "Mykola"
        resident.status = "deceased"
        db.update_resident(resident)
        updated = db.get_residents(addr.id)[0]
        assert updated.first_name == "Mykola"
        assert updated.status == "deceased"

    def test_delete_resident(self, db, addr, resident):
        db.delete_resident(resident.id)
        assert db.get_residents(addr.id) == []

    def test_mark_deceased(self, db, addr, resident):
        db.mark_deceased(resident.id, "2023-11-01")
        r = db.get_residents(addr.id)[0]
        assert r.status == "deceased"
        assert r.death_date == "2023-11-01"

    def test_mark_left(self, db, addr, resident):
        db.mark_left(resident.id)
        r = db.get_residents(addr.id)[0]
        assert r.status == "left"

    def test_active_count_excludes_deceased(self, db, addr, resident):
        db.mark_deceased(resident.id, "2023-01-01")
        addresses = db.get_addresses()
        assert addresses[0].active_count == 0

    def test_active_count_excludes_left(self, db, addr, resident):
        db.mark_left(resident.id)
        addresses = db.get_addresses()
        assert addresses[0].active_count == 0

    def test_resident_all_fields_roundtrip(self, db, addr):
        r = Resident(
            id=None, address_id=addr.id,
            first_name="Petro", last_name="Savchenko",
            birth_date="1965-07-20", baptism_date="1965-08-01",
            marriage_date="1990-09-15", death_date=None,
            status="active", father="Vasyl", mother="Halyna",
            spouse="Olena", notes="Elder of the church"
        )
        added = db.add_resident(r)
        fetched = db.get_residents(addr.id)[0]
        assert fetched.birth_date == "1965-07-20"
        assert fetched.baptism_date == "1965-08-01"
        assert fetched.marriage_date == "1990-09-15"
        assert fetched.father == "Vasyl"
        assert fetched.mother == "Halyna"
        assert fetched.spouse == "Olena"
        assert fetched.notes == "Elder of the church"


# ── Events ────────────────────────────────────────────────────────────────────

class TestEvents:
    def test_add_event_assigns_id(self, db, resident):
        ev = Event(id=None, resident_id=resident.id, event_type="birth", event_date="1980-04-10")
        added = db.add_event(ev)
        assert added.id is not None

    def test_get_events_for_address(self, db, addr, resident):
        ev = Event(id=None, resident_id=resident.id, event_type="baptism",
                   event_date="1980-05-01", description="Holy Spirit")
        db.add_event(ev)
        events = db.get_events_for_address(addr.id)
        assert len(events) == 1
        assert events[0].event_type == "baptism"
        assert events[0].description == "Holy Spirit"

    def test_get_events_includes_resident_name(self, db, addr, resident):
        db.add_event(Event(id=None, resident_id=resident.id,
                           event_type="marriage", event_date="2005-06-10"))
        events = db.get_events_for_address(addr.id)
        assert events[0].resident_name == "Ivan Kovalenko"

    def test_get_events_sorted_by_date_desc(self, db, addr, resident):
        db.add_event(Event(id=None, resident_id=resident.id,
                           event_type="birth", event_date="1980-04-10"))
        db.add_event(Event(id=None, resident_id=resident.id,
                           event_type="baptism", event_date="1980-05-01"))
        events = db.get_events_for_address(addr.id)
        assert events[0].event_date >= events[1].event_date

    def test_get_events_empty_for_unknown_address(self, db):
        assert db.get_events_for_address(9999) == []

    def test_delete_resident_cascades_to_events(self, db, addr, resident):
        db.add_event(Event(id=None, resident_id=resident.id,
                           event_type="birth", event_date="1980-04-10"))
        db.delete_resident(resident.id)
        assert db.get_events_for_address(addr.id) == []
