import pytest

from app.domain.models import (
    ReviewDecision,
    ReviewRequest,
    SegmentDecision,
    ValidationSegment,
)
from app.domain.review import InvalidReviewDecision, resolve_review


@pytest.fixture
def review_request() -> ReviewRequest:
    return ReviewRequest(
        review_request_id="review:validation:run-1:1",
        revision=1,
        segments=[
            ValidationSegment(
                segment_id="s1",
                original_text="one",
                first_translation="하나 초안",
                validated_translation="하나 검증",
                validation_note="교정",
            ),
            ValidationSegment(
                segment_id="s2",
                original_text="two",
                first_translation="둘 초안",
                validated_translation="둘 검증",
                validation_note="교정",
            ),
            ValidationSegment(
                segment_id="s3",
                original_text="three",
                first_translation="셋 초안",
                validated_translation="셋 검증",
                validation_note="교정",
            ),
        ],
    )


def test_resolve_review_supports_all_selection_types(review_request):
    decision = ReviewDecision(
        review_request_id=review_request.review_request_id,
        revision=1,
        decisions=[
            SegmentDecision(segment_id="s1", selected="first"),
            SegmentDecision(segment_id="s2", selected="validated"),
            SegmentDecision(segment_id="s3", selected="custom", custom_text="직접 수정"),
        ],
    )

    result = resolve_review(review_request, decision)

    assert [item.translated_text for item in result] == ["하나 초안", "둘 검증", "직접 수정"]


@pytest.mark.parametrize(
    "decision",
    [
        ReviewDecision(
            review_request_id="wrong",
            revision=1,
            decisions=[SegmentDecision(segment_id="s1", selected="first")],
        ),
        ReviewDecision(
            review_request_id="review:validation:run-1:1",
            revision=2,
            decisions=[SegmentDecision(segment_id="s1", selected="first")],
        ),
        ReviewDecision(
            review_request_id="review:validation:run-1:1",
            revision=1,
            decisions=[SegmentDecision(segment_id="missing", selected="first")],
        ),
    ],
)
def test_resolve_review_rejects_mismatched_decisions(review_request, decision):
    with pytest.raises(InvalidReviewDecision):
        resolve_review(review_request, decision)


def test_resolve_review_requires_every_segment(review_request):
    decision = ReviewDecision(
        review_request_id=review_request.review_request_id,
        revision=1,
        decisions=[SegmentDecision(segment_id="s1", selected="first")],
    )
    with pytest.raises(InvalidReviewDecision, match="모든 segment"):
        resolve_review(review_request, decision)
