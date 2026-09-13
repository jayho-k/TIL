from app.domain.models import FinalTranslation, ReviewDecision, ReviewRequest


class InvalidReviewDecision(ValueError):
    pass


def resolve_review(
    request: ReviewRequest,
    decision: ReviewDecision,
) -> list[FinalTranslation]:
    if decision.review_request_id != request.review_request_id:
        raise InvalidReviewDecision("review_request_id가 일치하지 않습니다.")
    if decision.revision != request.revision:
        raise InvalidReviewDecision("revision이 일치하지 않습니다.")

    requested = {item.segment_id: item for item in request.segments}
    received: dict[str, object] = {}
    for item in decision.decisions:
        if item.segment_id not in requested:
            raise InvalidReviewDecision(f"알 수 없는 segment: {item.segment_id}")
        if item.segment_id in received:
            raise InvalidReviewDecision(f"중복 segment: {item.segment_id}")
        received[item.segment_id] = item

    if set(received) != set(requested):
        raise InvalidReviewDecision("모든 segment에 대한 결정이 필요합니다.")

    result: list[FinalTranslation] = []
    for candidate in request.segments:
        item = received[candidate.segment_id]
        if item.selected == "first":  # type: ignore[union-attr]
            text = candidate.first_translation
        elif item.selected == "validated":  # type: ignore[union-attr]
            text = candidate.validated_translation
        else:
            text = (item.custom_text or "").strip()  # type: ignore[union-attr]
            if not text:
                raise InvalidReviewDecision("custom 선택에는 번역문이 필요합니다.")
        result.append(FinalTranslation(segment_id=candidate.segment_id, translated_text=text))
    return result
