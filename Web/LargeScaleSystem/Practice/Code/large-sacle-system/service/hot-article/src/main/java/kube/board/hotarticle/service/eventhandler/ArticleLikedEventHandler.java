package kube.board.hotarticle.service.eventhandler;

import kube.board.common.event.Event;
import kube.board.common.event.EventType;
import kube.board.common.event.payload.ArticleLikedEventPayload;
import kube.board.hotarticle.repository.ArticleLikeCountRepository;
import kube.board.hotarticle.utils.TimeCalculatorUtils;
import lombok.RequiredArgsConstructor;
import org.springframework.stereotype.Component;
import org.springframework.stereotype.Repository;

@Component
@RequiredArgsConstructor
public class ArticleLikedEventHandler implements EventHandler<ArticleLikedEventPayload> {
    private final ArticleLikeCountRepository articleLikeCountRepository;

    @Override
    public void handler(Event<ArticleLikedEventPayload> event) {
        ArticleLikedEventPayload payload = event.getPayload();
        articleLikeCountRepository.createOrUpdate(
                payload.getArticleId(),
                payload.getArticleLikeCount(),
                TimeCalculatorUtils.calculateDurationToMidnight()
        );
    }

    @Override
    public boolean supports(Event<ArticleLikedEventPayload> event) {
        return EventType.ARTICLE_LIKE == event.getType();
    }

    @Override
    public Long findArticleId(Event<ArticleLikedEventPayload> event) {
        return event.getPayload().getArticleId();
    }
}
