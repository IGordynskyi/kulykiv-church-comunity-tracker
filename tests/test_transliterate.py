"""Tests for transliterate.py — Ukrainian ↔ Latin helpers."""
import pytest
from transliterate import uk_to_en, normalize_for_search


class TestUkToEn:
    """Character-level transliteration: uk_to_en()."""

    # ── vowels ────────────────────────────────────────────────────────────────

    def test_simple_vowels_lowercase(self):
        assert uk_to_en("аеіоу") == "aeiou"

    def test_simple_vowels_uppercase(self):
        assert uk_to_en("АЕІОУ") == "aeiou"

    def test_ye_vowel_lowercase(self):
        assert uk_to_en("є") == "ye"

    def test_ye_vowel_uppercase(self):
        assert uk_to_en("Є") == "ye"

    def test_yi_vowel_lowercase(self):
        assert uk_to_en("ї") == "yi"

    def test_yi_vowel_uppercase(self):
        assert uk_to_en("Ї") == "yi"

    def test_yu_vowel(self):
        assert uk_to_en("ю") == "yu"
        assert uk_to_en("Ю") == "yu"

    def test_ya_vowel(self):
        assert uk_to_en("я") == "ya"
        assert uk_to_en("Я") == "ya"

    def test_y_vowel(self):
        assert uk_to_en("и") == "y"
        assert uk_to_en("И") == "y"

    def test_i_vowel(self):
        assert uk_to_en("і") == "i"
        assert uk_to_en("І") == "i"

    # ── consonants ────────────────────────────────────────────────────────────

    def test_simple_consonants_lowercase(self):
        pairs = [
            ("б", "b"), ("в", "v"), ("г", "h"), ("ґ", "g"), ("д", "d"),
            ("з", "z"), ("к", "k"), ("л", "l"), ("м", "m"), ("н", "n"),
            ("п", "p"), ("р", "r"), ("с", "s"), ("т", "t"), ("ф", "f"),
        ]
        for uk, en in pairs:
            assert uk_to_en(uk) == en, f"uk_to_en({uk!r}) should be {en!r}"

    def test_simple_consonants_uppercase(self):
        pairs = [
            ("Б", "b"), ("В", "v"), ("Г", "h"), ("Ґ", "g"), ("Д", "d"),
            ("З", "z"), ("К", "k"), ("Л", "l"), ("М", "m"), ("Н", "n"),
            ("П", "p"), ("Р", "r"), ("С", "s"), ("Т", "t"), ("Ф", "f"),
        ]
        for uk, en in pairs:
            assert uk_to_en(uk) == en, f"uk_to_en({uk!r}) should be {en!r}"

    def test_digraph_zh(self):
        assert uk_to_en("ж") == "zh"
        assert uk_to_en("Ж") == "zh"

    def test_digraph_kh(self):
        assert uk_to_en("х") == "kh"
        assert uk_to_en("Х") == "kh"

    def test_digraph_ts(self):
        assert uk_to_en("ц") == "ts"
        assert uk_to_en("Ц") == "ts"

    def test_digraph_ch(self):
        assert uk_to_en("ч") == "ch"
        assert uk_to_en("Ч") == "ch"

    def test_digraph_sh(self):
        assert uk_to_en("ш") == "sh"
        assert uk_to_en("Ш") == "sh"

    def test_digraph_shch(self):
        assert uk_to_en("щ") == "shch"
        assert uk_to_en("Щ") == "shch"

    def test_soft_sign_produces_empty_string(self):
        assert uk_to_en("ь") == ""
        assert uk_to_en("Ь") == ""

    def test_y_consonant(self):
        assert uk_to_en("й") == "y"
        assert uk_to_en("Й") == "y"

    # ── full words ────────────────────────────────────────────────────────────
    # Note: uppercase Cyrillic is mapped to *lowercase* Latin in the table,
    # because uk_to_en() is designed to be consumed by normalize_for_search()
    # which lowercases the result anyway. Use normalize_for_search() when
    # case-insensitive comparison is the goal.

    def test_word_ivan(self):
        assert uk_to_en("Іван") == "ivan"

    def test_word_shevchenko(self):
        assert uk_to_en("Шевченко") == "shevchenko"

    def test_word_koval(self):
        # Коваль — soft sign disappears
        assert uk_to_en("Коваль") == "koval"

    def test_word_kulykiv(self):
        assert uk_to_en("Куликів") == "kulykiv"

    def test_word_bohorodytsia(self):
        assert uk_to_en("Богородиця") == "bohorodytsya"

    # ── passthrough behaviour ─────────────────────────────────────────────────

    def test_latin_passthrough(self):
        # Latin characters are not in the table → pass through unchanged
        assert uk_to_en("Ivan") == "Ivan"

    def test_digits_passthrough(self):
        assert uk_to_en("123") == "123"

    def test_spaces_passthrough(self):
        # Cyrillic is lowercased; Latin spaces pass through
        assert uk_to_en("Іван Коваль") == "ivan koval"

    def test_street_name_with_number(self):
        # "Шевченка" is the genitive form → "shevchenka"
        assert uk_to_en("Шевченка, 5") == "shevchenka, 5"

    def test_empty_string(self):
        assert uk_to_en("") == ""

    def test_mixed_scripts(self):
        # Latin "Ivan" passes through; Cyrillic "Іванченко" is lowercased
        result = uk_to_en("Ivan Іванченко")
        assert result == "Ivan ivanchenko"


class TestNormalizeForSearch:
    """normalize_for_search() — transliterate + lowercase."""

    def test_ukrainian_lowercased(self):
        assert normalize_for_search("Іван") == "ivan"

    def test_latin_lowercased(self):
        assert normalize_for_search("Ivan") == "ivan"

    def test_cyrillic_uppercase_lowercased(self):
        assert normalize_for_search("ІВАН") == "ivan"

    def test_latin_uppercase_lowercased(self):
        assert normalize_for_search("IVAN") == "ivan"

    def test_shevchenko(self):
        assert normalize_for_search("Шевченко") == "shevchenko"
        assert normalize_for_search("shevchenko") == "shevchenko"
        assert normalize_for_search("SHEVCHENKO") == "shevchenko"

    def test_empty_string(self):
        assert normalize_for_search("") == ""

    def test_spaces_preserved(self):
        result = normalize_for_search("Іван Коваль")
        assert result == "ivan koval"

    # ── cross-script search simulation ────────────────────────────────────────

    @pytest.mark.parametrize("query,name", [
        ("ivan",     "Іван Коваль"),
        ("Іван",     "Ivan Koval"),
        ("koval",    "Коваль Іван"),
        ("Коваль",   "Koval Ivan"),
        ("shevch",   "Шевченко Тарас"),
        ("шевч",     "Shevchenko Taras"),
        ("ivan",     "Іван Шевченко"),
        ("taras",    "Тарас Шевченко"),
    ])
    def test_cross_script_match(self, query, name):
        """Normalized query must be a substring of the normalized name."""
        assert normalize_for_search(query) in normalize_for_search(name)

    @pytest.mark.parametrize("query,name", [
        ("petro",    "Іван Коваль"),
        ("Петро",    "Ivan Koval"),
        ("xyz",      "Шевченко Тарас"),
    ])
    def test_cross_script_no_match(self, query, name):
        """Non-matching query must not appear in the normalized name."""
        assert normalize_for_search(query) not in normalize_for_search(name)

    def test_both_scripts_produce_same_result(self):
        """Ukrainian and its Latin transliteration must normalize identically."""
        assert normalize_for_search("Іван") == normalize_for_search("Ivan")
        assert normalize_for_search("Шевченко") == normalize_for_search("Shevchenko")
        assert normalize_for_search("Коваль") == normalize_for_search("Koval")

    def test_address_search_cyrillic_query(self):
        street = "Шевченка 5"
        assert normalize_for_search("шевч") in normalize_for_search(street)

    def test_address_search_latin_query(self):
        street = "Шевченка 5"
        assert normalize_for_search("shevch") in normalize_for_search(street)

    def test_soft_sign_transparent_in_search(self):
        # "Коваль" and "Koval" must match each other
        koval_uk = normalize_for_search("Коваль")   # soft sign drops → "koval"
        koval_en = normalize_for_search("Koval")
        assert koval_uk == koval_en
