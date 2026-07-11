from app.integrations.captions import generate_ass_subtitles


def test_generates_ass_header():
    result = generate_ass_subtitles([], 0.0, 10.0)
    assert "[Script Info]" in result
    assert "[V4+ Styles]" in result
    assert "[Events]" in result


def test_segment_timestamps_offset_by_clip_start():
    segments = [{"start": 10.0, "end": 15.0, "text": "Hello world"}]
    result = generate_ass_subtitles(segments, 10.0, 60.0)
    # Relative start = 10.0 - 10.0 = 0.0 → 0:00:00.00
    # Relative end   = 15.0 - 10.0 = 5.0 → 0:00:05.00
    assert "0:00:00.00" in result
    assert "0:00:05.00" in result
    assert "Hello world" in result


def test_segments_outside_clip_window_excluded():
    segments = [
        {"start": 0.0, "end": 5.0, "text": "Before"},
        {"start": 10.0, "end": 20.0, "text": "Inside"},
        {"start": 55.0, "end": 65.0, "text": "After"},
    ]
    result = generate_ass_subtitles(segments, 10.0, 50.0)
    assert "Before" not in result
    assert "Inside" in result
    assert "After" not in result


def test_empty_text_segments_excluded():
    segments = [{"start": 10.0, "end": 15.0, "text": "   "}]
    result = generate_ass_subtitles(segments, 10.0, 60.0)
    assert "Dialogue:" not in result


def test_ass_special_chars_escaped():
    segments = [{"start": 10.0, "end": 15.0, "text": "Hello {bold} world"}]
    result = generate_ass_subtitles(segments, 10.0, 60.0)
    assert "\\{bold\\}" in result


def test_time_format_centiseconds():
    segments = [{"start": 10.5, "end": 11.75, "text": "Test"}]
    result = generate_ass_subtitles(segments, 10.0, 60.0)
    # Relative start = 0.5s → 0:00:00.50
    # Relative end = 1.75s → 0:00:01.75
    assert "0:00:00.50" in result
    assert "0:00:01.75" in result
