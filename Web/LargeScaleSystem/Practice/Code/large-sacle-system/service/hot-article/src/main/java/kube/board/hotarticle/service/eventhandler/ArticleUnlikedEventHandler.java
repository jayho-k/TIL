package kube.board.hotarticle.service.eventhandler;

import kube.board.common.event.Event;
import kube.board.common.event.EventType;
import kube.board.common.event.payload.ArticleUnlikedEventPayload;
import kube.board.hotarticle.repository.ArticleLikeCountRepository;
import kube.board.hotarticle.utils.TimeCalculatorUtils;
import lombok.RequiredArgsConstructor;
import org.springframework.stereotype.Component;

@Component
@RequiredArgsConstructor
public class ArticleUnlikedEventHandler implements EventHandler<ArticleUnlikedEventPayload> {
    private final ArticleLikeCountRepository articleLikeCountRepository;

    @Override
    public void handler(Event<ArticleUnlikedEventPayload> event) {
        ArticleUnlikedEventPayload payload = event.getPayload();
        articleLikeCountRepository.createOrUpdate(
                payload.getArticleId(),
                payload.getArticleLikeCount(),
                TimeCalculatorUtils.calculateDurationToMidnight()
        );
    }

    @Override
    public boolean supports(Event<ArticleUnlikedEventPayload> event) {
        return EventType.ARTICLE_UNLIKED == event.getType();
    }

    @Override
    public Long findArticleId(Event<ArticleUnlikedEventPayload> event) {
        return event.getPayload().getArticleId();
    }
}
