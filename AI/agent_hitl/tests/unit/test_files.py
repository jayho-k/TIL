import pytest

from app.storage.files import InvalidTextEncoding, parse_txt, render_txt


def test_txt_round_trip_preserves_blank_lines():
    source = "First paragraph.\n\nSecond paragraph.\n"
    parsed = parse_txt(source.encode("utf-8"))

    assert [item.segment_id for item in parsed.segments] == ["segment-0001", "segment-0002"]
    assert render_txt(parsed, ["첫 문단.", "둘째 문단."]) == "첫 문단.\n\n둘째 문단.\n"


def test_parse_txt_rejects_invalid_utf8():
    with pytest.raises(InvalidTextEncoding):
        parse_txt(b"\xff\xfe")
