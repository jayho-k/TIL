package kube.board.hotarticle.service.eventhandler;

import kube.board.common.event.Event;
import kube.board.common.event.EventPayload;
import kube.board.common.event.EventType;
import kube.board.common.event.payload.ArticleDeletedEventPayload;
import kube.board.hotarticle.repository.ArticleCreatedTimeRepository;
import kube.board.hotarticle.repository.HotArticleListRepository;
import lombok.RequiredArgsConstructor;
import org.springframework.stereotype.Component;

@Component
@RequiredArgsConstructor
public class ArticleDeletedEventHandler implements EventHandler<ArticleDeletedEventPayload>{

    private final HotArticleListRepository hotArticleListRepository;
    private final ArticleCreatedTimeRepository articleCreatedTimeRepository;

    @Override
    public void handler(Event<ArticleDeletedEventPayload> event) {
        ArticleDeletedEventPayload payload = event.getPayload();
        articleCreatedTimeRepository.delete(payload.getArticleId());
        hotArticleListRepository.remove(payload.getArticleId(), payload.getCreatedAt());

    }

    @Override
    public boolean supports(Event<ArticleDeletedEventPayload> event) {
        return EventType.ARTICLE_DELETED == event.getType();
    }

    @Override
    public Long findArticleId(Event<ArticleDeletedEventPayload> event) {
        return event.getPayload().getArticleId();
    }
}
