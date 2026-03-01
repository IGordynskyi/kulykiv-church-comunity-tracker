"""Tests for models.py — Address, Resident, Event dataclasses."""
import pytest
from models import Address, Resident, Event


class TestAddress:
    def test_basic_creation(self):
        addr = Address(id=1, street="Main St 5")
        assert addr.id == 1
        assert addr.street == "Main St 5"
        assert addr.notes == ""
        assert addr.active_count == 0

    def test_with_all_fields(self):
        addr = Address(id=2, street="Oak Ave 10", notes="Corner house", active_count=3)
        assert addr.notes == "Corner house"
        assert addr.active_count == 3

    def test_id_can_be_none(self):
        addr = Address(id=None, street="Shevchenko 7")
        assert addr.id is None


class TestResident:
    def _make(self, **kwargs):
        defaults = dict(
            id=1, address_id=10, first_name="Ivan", last_name="Kovalenko"
        )
        defaults.update(kwargs)
        return Resident(**defaults)

    def test_full_name(self):
        r = self._make(first_name="Maria", last_name="Petrenko")
        assert r.full_name == "Maria Petrenko"

    def test_is_baptized_true(self):
        r = self._make(baptism_date="2000-06-15")
        assert r.is_baptized is True

    def test_is_baptized_false(self):
        r = self._make(baptism_date=None)
        assert r.is_baptized is False

    def test_is_married_via_date(self):
        r = self._make(marriage_date="2010-08-20")
        assert r.is_married is True

    def test_is_married_via_spouse(self):
        r = self._make(marriage_date=None, spouse="Olena")
        assert r.is_married is True

    def test_is_married_neither(self):
        r = self._make(marriage_date=None, spouse=None)
        assert r.is_married is False

    def test_is_married_empty_spouse(self):
        r = self._make(marriage_date=None, spouse="")
        assert r.is_married is False

    def test_default_status(self):
        r = self._make()
        assert r.status == "active"

    def test_all_optional_fields_default_none(self):
        r = self._make()
        assert r.birth_date is None
        assert r.baptism_date is None
        assert r.marriage_date is None
        assert r.death_date is None
        assert r.father is None
        assert r.mother is None
        assert r.spouse is None

    def test_notes_default_empty(self):
        r = self._make()
        assert r.notes == ""


class TestEvent:
    def test_basic_creation(self):
        ev = Event(id=1, resident_id=5, event_type="birth", event_date="1990-03-10")
        assert ev.id == 1
        assert ev.resident_id == 5
        assert ev.event_type == "birth"
        assert ev.event_date == "1990-03-10"
        assert ev.description == ""
        assert ev.created_at == ""
        assert ev.resident_name == ""

    def test_with_all_fields(self):
        ev = Event(
            id=2, resident_id=7, event_type="marriage",
            event_date="2015-05-20", description="Big celebration",
            created_at="2015-05-21 10:00:00", resident_name="Ivan Kovalenko"
        )
        assert ev.description == "Big celebration"
        assert ev.resident_name == "Ivan Kovalenko"

    def test_id_can_be_none(self):
        ev = Event(id=None, resident_id=1, event_type="death", event_date="2023-01-01")
        assert ev.id is None
