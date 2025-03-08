package kube.board.hotarticle.service.eventhandler;

import kube.board.common.event.Event;
import kube.board.common.event.EventType;
import kube.board.common.event.payload.ArticleCreatedEventPayload;
import kube.board.hotarticle.repository.ArticleCreatedTimeRepository;
import kube.board.hotarticle.utils.TimeCalculatorUtils;
import lombok.RequiredArgsConstructor;
import org.springframework.stereotype.Component;

@Component
@RequiredArgsConstructor
public class ArticleCreatedEventHandler implements EventHandler<ArticleCreatedEventPayload>{

    private final ArticleCreatedTimeRepository articleCreatedTimeRepository;

    @Override
    public void handler(Event<ArticleCreatedEventPayload> event) {
        ArticleCreatedEventPayload payload = event.getPayload();
        articleCreatedTimeRepository.createOrUpdate(
                payload.getArticleId(),
                payload.getCreatedAt(),
                TimeCalculatorUtils.calculateDurationToMidnight()
        );
    }

    @Override
    public boolean supports(Event<ArticleCreatedEventPayload> event) {
        return EventType.ARTICLE_CREATED == event.getType();
    }

    @Override
    public Long findArticleId(Event<ArticleCreatedEventPayload> event) {
        return event.getPayload().getArticleId();
    }
}
