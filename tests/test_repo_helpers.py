import pytest

from app.commands.repo import format_description, format_languages, format_size, format_topics


def test_format_topics():
    assert format_topics(["a", "b"], 5) == "a, b"
    assert format_topics(["a", "b", "c"], 2) == "a, b + 1 more..."
    assert format_topics([]) == ""


def test_format_description_boundaries():
    assert format_description("short", 10) == "short"
    assert format_description("one two three four", 10) == "one two three..."
    assert format_description("abcdefghijklmnop", 5) == "abcde..."


@pytest.mark.parametrize("value, expected", [(0, "0.0 KB"), (999, "999.0 KB"), (1000, "1.0 MB"), (999_999, "1000.0 MB"), (1_000_000, "1.0 GB"), (1_000_000_000, "1.0 TB"), (1_000_000_000_000, "1.0 PB"), (1_000_000_000_000_000, "1000.0 PB")])
def test_format_size(value, expected):
    assert format_size(value) == expected


def test_format_languages():
    assert format_languages({}) == ["No language data returned."]
    assert format_languages({"Python": 3, "Rust": 1}) == ["Python: 75.0%", "Rust: 25.0%"]
    assert format_languages({"Python": 1, "Rust": 1, "Go": 1}, 2)[-1] == "+ 1 more..."
    assert format_languages({"Python": 10}) == ["Python: 100.0%"]
