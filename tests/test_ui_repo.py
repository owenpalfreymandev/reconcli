import pytest

from app.ui.repo import _contributor_row, _language_row, format_bytes, format_size


@pytest.mark.parametrize(
    "value, expected",
    [
        (0, "0.0 KB"),
        (999, "999.0 KB"),
        (1000, "1.0 MB"),
        (999_999, "1000.0 MB"),
        (1_000_000, "1.0 GB"),
        (1_000_000_000, "1.0 TB"),
        (1_000_000_000_000, "1.0 PB"),
        (1_000_000_000_000_000, "1000.0 PB"),
    ],
)
def test_ui_format_size(value, expected):
    assert format_size(value) == expected


@pytest.mark.parametrize(
    "value, expected",
    [
        (0, "0 B"),
        (999, "999 B"),
        (1000, "1.0 KB"),
        (999_999, "1000.0 KB"),
        (1_000_000, "1.0 MB"),
        (1_000_000_000, "1.0 GB"),
        (1_000_000_000_000, "1.0 TB"),
    ],
)
def test_format_bytes(value, expected):
    assert format_bytes(value) == expected
    assert format_bytes(None) == "Not available"


def test_bars_scale_and_zero_is_safe():
    full = _contributor_row(
        {"login": "full", "commits": 10}, 10, 10
    ).plain.splitlines()[1]
    half = _contributor_row({"login": "half", "commits": 5}, 10, 10).plain.splitlines()[
        1
    ]
    zero = _contributor_row({"login": "zero", "commits": 0}, 10, 10).plain.splitlines()[
        1
    ]
    assert full.count("█") == 32
    assert half.count("█") == 16
    assert zero.count("█") == 0

    language = _language_row("Python", 5, 10, 10)
    assert language.plain.splitlines()[1].count("█") == 16
    assert _language_row("Empty", 0, 10, 10).plain.splitlines()[1].count("█") == 0
