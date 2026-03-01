"""Tests for lang.py — i18n/l10n helpers."""
import pytest
import lang


@pytest.fixture(autouse=True)
def reset_lang():
    """Reset language to English before each test."""
    lang.set_lang("en")
    yield
    lang.set_lang("en")


class TestSetLang:
    def test_set_english(self):
        lang.set_lang("en")
        assert lang.current() == "en"

    def test_set_ukrainian(self):
        lang.set_lang("uk")
        assert lang.current() == "uk"

    def test_invalid_lang_ignored(self):
        lang.set_lang("en")
        lang.set_lang("fr")  # unsupported
        assert lang.current() == "en"

    def test_empty_string_ignored(self):
        lang.set_lang("en")
        lang.set_lang("")
        assert lang.current() == "en"


class TestGet:
    def test_known_key_english(self):
        lang.set_lang("en")
        assert lang.get("save") == "Save"

    def test_known_key_ukrainian(self):
        lang.set_lang("uk")
        assert lang.get("save") == "Зберегти"

    def test_missing_key_returns_bracket_form(self):
        result = lang.get("nonexistent_key_xyz")
        assert result == "[nonexistent_key_xyz]"

    def test_format_substitution(self):
        lang.set_lang("en")
        result = lang.get("status_viewing", street="Oak Ave 10", count=3)
        assert "Oak Ave 10" in result
        assert "3" in result

    def test_format_substitution_ukrainian(self):
        lang.set_lang("uk")
        result = lang.get("status_viewing", street="Шевченка 5", count=2)
        assert "Шевченка 5" in result
        assert "2" in result

    def test_no_kwargs_returns_plain_string(self):
        lang.set_lang("en")
        result = lang.get("cancel")
        assert result == "Cancel"

    def test_about_text_multiline(self):
        lang.set_lang("en")
        text = lang.get("about_text")
        assert "Version" in text

    def test_app_title_english(self):
        lang.set_lang("en")
        title = lang.get("app_title")
        assert len(title) > 0

    def test_app_title_ukrainian_differs_from_english(self):
        lang.set_lang("en")
        en_title = lang.get("app_title")
        lang.set_lang("uk")
        uk_title = lang.get("app_title")
        assert len(uk_title) > 0
        assert uk_title != en_title


class TestEventTypes:
    def test_returns_four_items_en(self):
        lang.set_lang("en")
        types = lang.event_types()
        assert len(types) == 4

    def test_returns_four_items_uk(self):
        lang.set_lang("uk")
        types = lang.event_types()
        assert len(types) == 4

    def test_english_event_types(self):
        lang.set_lang("en")
        types = lang.event_types()
        assert "birth" in types
        assert "baptism" in types
        assert "marriage" in types
        assert "death" in types

    def test_ukrainian_event_types(self):
        lang.set_lang("uk")
        types = lang.event_types()
        assert "народження" in types
        assert "хрещення" in types
        assert "шлюб" in types
        assert "смерть" in types


class TestEventTypeToKey:
    def test_english_localized_to_key(self):
        lang.set_lang("en")
        assert lang.event_type_to_key("birth") == "birth"
        assert lang.event_type_to_key("baptism") == "baptism"
        assert lang.event_type_to_key("marriage") == "marriage"
        assert lang.event_type_to_key("death") == "death"

    def test_ukrainian_localized_to_key(self):
        lang.set_lang("uk")
        assert lang.event_type_to_key("народження") == "birth"
        assert lang.event_type_to_key("хрещення") == "baptism"
        assert lang.event_type_to_key("шлюб") == "marriage"
        assert lang.event_type_to_key("смерть") == "death"

    def test_bare_english_key_passthrough(self):
        lang.set_lang("uk")
        # DB may store bare EN keys — must map correctly
        assert lang.event_type_to_key("birth") == "birth"
        assert lang.event_type_to_key("death") == "death"

    def test_unknown_returns_itself(self):
        result = lang.event_type_to_key("unknown_event")
        assert result == "unknown_event"


class TestEventKeyToLabel:
    def test_english_labels(self):
        lang.set_lang("en")
        assert lang.event_key_to_label("birth") == "birth"
        assert lang.event_key_to_label("baptism") == "baptism"
        assert lang.event_key_to_label("marriage") == "marriage"
        assert lang.event_key_to_label("death") == "death"

    def test_ukrainian_labels(self):
        lang.set_lang("uk")
        assert lang.event_key_to_label("birth") == "народження"
        assert lang.event_key_to_label("baptism") == "хрещення"
        assert lang.event_key_to_label("marriage") == "шлюб"
        assert lang.event_key_to_label("death") == "смерть"

    def test_unknown_key_passthrough(self):
        result = lang.event_key_to_label("mystery")
        assert result == "mystery"
