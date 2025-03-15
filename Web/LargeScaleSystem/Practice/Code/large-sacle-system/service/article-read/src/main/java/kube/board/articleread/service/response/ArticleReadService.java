package kube.board.articleread.service.response;

import kube.board.articleread.client.ArticleClient;
import kube.board.articleread.client.CommentClient;
import kube.board.articleread.client.LikeClient;
import kube.board.articleread.client.ViewClient;
import kube.board.articleread.repository.ArticleQueryModel;
import kube.board.articleread.repository.ArticleQueryModelRepository;
import kube.board.articleread.service.ArticleReadResponse;
import kube.board.articleread.service.event.hadler.EventHandler;
import kube.board.common.event.Event;
import kube.board.common.event.EventPayload;
import lombok.RequiredArgsConstructor;
import lombok.extern.slf4j.Slf4j;
import org.springframework.stereotype.Service;

import java.time.Duration;
import java.util.List;
import java.util.Optional;

@Slf4j
@Service
@RequiredArgsConstructor
public class ArticleReadService {

    private final ArticleClient articleClient;
    private final CommentClient commentClient;
    private final LikeClient likeClient;
    private final ViewClient viewClient;
    private final ArticleQueryModelRepository articleQueryModelRepository;
    private final List<EventHandler> eventHandlers;

    public void handleEvent(Event<EventPayload> event){
        for (EventHandler eventHandler : eventHandlers){
            eventHandler.handler(event);
        }
    }

    public ArticleReadResponse read(Long articleId){
        // redis에 있으면 가져오고 없으면 client 요청
        ArticleQueryModel articleQueryModel = articleQueryModelRepository.read(articleId)
                .or(() -> fetch(articleId)) // fetch : 다른 서비스들에게 요청하는 부분
                .orElseThrow();

        return ArticleReadResponse.from(
                articleQueryModel,
                viewClient.count(articleId)
        );
    }

    private Optional<ArticleQueryModel> fetch(Long articleId){
        Optional<ArticleQueryModel> articleQueryModelOptional = articleClient.read(articleId)
                .map(article -> ArticleQueryModel.create(
                        article,
                        commentClient.count(articleId),
                        likeClient.count(articleId)
                ));

        articleQueryModelOptional
                .ifPresent(articleQueryModel -> articleQueryModelRepository.create(articleQueryModel, Duration.ofDays(1)));
        log.info("[ArticleReadService.fetch] fetch data. articleId={}, isPresent={}", articleId, articleQueryModelOptional.isPresent());
        return articleQueryModelOptional;
    }

}
