package kube.board.hotarticle.service;

import kube.board.common.event.Event;
import kube.board.common.event.EventPayload;
import kube.board.common.event.EventType;
import kube.board.hotarticle.client.ArticleClient;
import kube.board.hotarticle.repository.HotArticleListRepository;
import kube.board.hotarticle.service.eventhandler.EventHandler;
import kube.board.hotarticle.service.response.HotArticleResponse;
import lombok.RequiredArgsConstructor;
import lombok.extern.slf4j.Slf4j;
import org.springframework.stereotype.Service;

import java.util.List;
import java.util.Objects;

@Slf4j
@Service
@RequiredArgsConstructor
public class HotArticleService {

    private final ArticleClient articleClient;
    private final List<EventHandler> eventHandlers;
    private final HotArticleScoreUpdater hotArticleScoreUpdater;
    private final HotArticleListRepository hotArticleListRepository;

    public void handleEvent(Event<EventPayload> event){

        EventHandler<EventPayload> eventHandler = findEventHandler(event);
        if (eventHandler == null){
            return;
        }

        if (isArticleCreatedOrDeleted(event)){
            eventHandler.handler(event);
        }else {
            hotArticleScoreUpdater.update(event, eventHandler);
        }
    }

    private boolean isArticleCreatedOrDeleted(Event<EventPayload> event) {
        return EventType.ARTICLE_CREATED == event.getType() || EventType.ARTICLE_DELETED == event.getType();
    }

    private EventHandler<EventPayload> findEventHandler(Event<EventPayload> event){
        return eventHandlers.stream()
                .filter(eventHandler -> eventHandler.supports(event))
                .findAny()
                .orElse(null);
    }

    public List<HotArticleResponse> readAll(String dateStr){
        return hotArticleListRepository.readAll(dateStr).stream()
                .map(articleClient::read)
                .filter(Objects::nonNull)
                .map(HotArticleResponse::from)
                .toList();
    }



}
