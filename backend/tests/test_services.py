from app.services.llm import analyze_match
from app.utils.text import chunk_text


def test_chunk_text_splits_on_double_newline():
    # test that a string with \n\n produces correct chunks
    text = "First paragraph here is long enough.\n\nSecond paragraph also long enough."
    res = chunk_text(text)
    assert len(res) == 2


def test_chunk_text_filters_short_chunks():
    text = "First paragraph here is long enough.\n\nSecond paragraph also long enough.Third\n\n is not"
    res = chunk_text(text)
    assert len(res) == 2


def test_analyze_match_returns_early_for_empty_chunks():
    result = analyze_match(jd_text="some job description", resume_chunks=[])
    assert result["match_score"] == 0
