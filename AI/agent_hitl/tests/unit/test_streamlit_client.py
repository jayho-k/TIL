from streamlit_app.client import parse_sse_lines


def test_parse_sse_lines_handles_multiple_events():
    lines = [
        "event: progress",
        'data: {"stage":"start"}',
        "",
        "event: completed",
        'data: {"download_url":"/runs/r1/download"}',
        "",
    ]
    assert list(parse_sse_lines(lines)) == [
        ("progress", {"stage": "start"}),
        ("completed", {"download_url": "/runs/r1/download"}),
    ]
