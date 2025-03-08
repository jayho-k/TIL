package kube.board.hotarticle.service;

import kube.board.common.event.Event;
import kube.board.common.event.EventPayload;
import kube.board.hotarticle.repository.ArticleCreatedTimeRepository;
import kube.board.hotarticle.repository.HotArticleListRepository;
import kube.board.hotarticle.service.eventhandler.EventHandler;
import lombok.RequiredArgsConstructor;
import org.springframework.stereotype.Component;

import java.time.Duration;
import java.time.LocalDate;
import java.time.LocalDateTime;

@Component
@RequiredArgsConstructor
public class HotArticleScoreUpdater {

    private final HotArticleListRepository hotArticleListRepository;
    private final HotArticleScoreCalculator hotArticleScoreCalculator;

    private final ArticleCreatedTimeRepository articleCreatedTimeRepository;

    private static final long HOT_ARTICLE_COUNT = 10;

    // 7일만 넘게 저장하고 있으면 Application 단에서 조절할 수 있기 때문에 넉넉히 잡는다.
    private static final Duration HOT_ARTICLE_TTL = Duration.ofDays(10);


    public void update(Event<EventPayload> event, EventHandler<EventPayload> eventHandler){
        Long articleId = eventHandler.findArticleId(event);
        LocalDateTime createdTime = articleCreatedTimeRepository.read(articleId);

        if (!isArticleCreatedToday(createdTime)) {
            return;
        }

        eventHandler.handler(event);

        long score = hotArticleScoreCalculator.calculate(articleId);
        hotArticleListRepository.add(
                articleId,
                createdTime,
                score,
                HOT_ARTICLE_COUNT,
                HOT_ARTICLE_TTL
        );
    }

    private boolean isArticleCreatedToday(LocalDateTime createdTime) {
        return createdTime != null && createdTime.toLocalDate().equals(LocalDate.now());
    }

}
