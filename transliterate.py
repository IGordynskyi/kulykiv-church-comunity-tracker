"""
Ukrainian ↔ Latin transliteration helpers.

Used to enable cross-script searching: typing Latin (e.g. "Ivan") finds
Cyrillic names (e.g. "Іван") and vice-versa.

Only uk_to_en is needed for search: both the query and the stored name are
converted to Latin, then compared — so whichever script the user types in,
the match works.
"""

# Simplified KMU-2010-based Ukrainian → Latin table, tuned for name matching.
# Multi-character outputs are intentional (zh, kh, ts, ch, sh, shch).
_UK_TO_EN: dict[str, str] = {
    # lowercase
    'а': 'a',   'б': 'b',   'в': 'v',   'г': 'h',   'ґ': 'g',
    'д': 'd',   'е': 'e',   'є': 'ye',  'ж': 'zh',  'з': 'z',
    'и': 'y',   'і': 'i',   'ї': 'yi',  'й': 'y',   'к': 'k',
    'л': 'l',   'м': 'm',   'н': 'n',   'о': 'o',   'п': 'p',
    'р': 'r',   'с': 's',   'т': 't',   'у': 'u',   'ф': 'f',
    'х': 'kh',  'ц': 'ts',  'ч': 'ch',  'ш': 'sh',  'щ': 'shch',
    'ь': '',    'ю': 'yu',  'я': 'ya',
    # uppercase (output is lowercase — normalize_for_search lowercases anyway)
    'А': 'a',   'Б': 'b',   'В': 'v',   'Г': 'h',   'Ґ': 'g',
    'Д': 'd',   'Е': 'e',   'Є': 'ye',  'Ж': 'zh',  'З': 'z',
    'И': 'y',   'І': 'i',   'Ї': 'yi',  'Й': 'y',   'К': 'k',
    'Л': 'l',   'М': 'm',   'Н': 'n',   'О': 'o',   'П': 'p',
    'Р': 'r',   'С': 's',   'Т': 't',   'У': 'u',   'Ф': 'f',
    'Х': 'kh',  'Ц': 'ts',  'Ч': 'ch',  'Ш': 'sh',  'Щ': 'shch',
    'Ь': '',    'Ю': 'yu',  'Я': 'ya',
}


def uk_to_en(text: str) -> str:
    """Transliterate Ukrainian Cyrillic characters to Latin equivalents.

    Non-Cyrillic characters (Latin, digits, spaces, punctuation) pass through
    unchanged, so mixed-script strings work correctly.
    """
    return ''.join(_UK_TO_EN.get(ch, ch) for ch in text)


def normalize_for_search(text: str) -> str:
    """Return a lowercase Latin string suitable for cross-script comparison.

    1. Transliterates any Ukrainian Cyrillic characters to Latin.
    2. Lowercases the result.

    Both the search query and the stored name should be processed with this
    function before comparing, so that:
      - "Ivan"  matches "Іван"
      - "іван"  matches "ivan"
      - "Koval" matches "Коваль"
    """
    return uk_to_en(text).lower()
