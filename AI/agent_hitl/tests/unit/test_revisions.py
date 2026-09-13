import pytest

from app.domain.models import ReviewRequest, ValidationSegment
from app.domain.revisions import apply_edits, content_hash, validate_action


def snapshot():
    return ReviewRequest(
        review_request_id="review:r:1:1",
        revision=1,
        snapshot_hash="snapshot",
        segments=[
            ValidationSegment(
                segment_id="s1",
                original_text="One",
                first_translation="하나",
                validated_translation="하나입니다",
                validation_note="격식",
            )
        ],
    )


def test_partial_edit_preserves_other_segments():
    current = {"s1": "하나", "s2": "둘"}
    assert apply_edits(current, {"s1": "하나입니다"}) == {"s1": "하나입니다", "s2": "둘"}
    assert current["s1"] == "하나"


@pytest.mark.parametrize("edits", [{"unknown": "text"}, {"s1": "  "}, {}])
def test_invalid_edit_rejected(edits):
    with pytest.raises(ValueError):
        apply_edits({"s1": "하나"}, edits)


def test_custom_cannot_bypass_revalidation():
    with pytest.raises(ValueError):
        validate_action(
            snapshot(),
            {
                "command_id": "c1",
                "review_request_id": "review:r:1:1",
                "revision": 1,
                "snapshot_hash": "snapshot",
                "action": "approve",
                "decisions": [{"segment_id": "s1", "selected": "custom", "custom_text": "new"}],
            },
        )


def test_hash_is_stable_and_content_sensitive():
    assert content_hash({"a": 1, "b": 2}) == content_hash({"b": 2, "a": 1})
    assert content_hash({"a": 1}) != content_hash({"a": 2})
