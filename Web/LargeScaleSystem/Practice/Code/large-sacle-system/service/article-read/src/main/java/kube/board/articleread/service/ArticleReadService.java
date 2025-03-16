package kube.board.articleread.service;

import kube.board.articleread.client.ArticleClient;
import kube.board.articleread.client.CommentClient;
import kube.board.articleread.client.LikeClient;
import kube.board.articleread.client.ViewClient;
import kube.board.articleread.repository.ArticleIdListRepository;
import kube.board.articleread.repository.ArticleQueryModel;
import kube.board.articleread.repository.ArticleQueryModelRepository;
import kube.board.articleread.repository.BoardArticleCountRepository;
import kube.board.articleread.service.event.hadler.EventHandler;
import kube.board.articleread.service.response.ArticleReadPageResponse;
import kube.board.articleread.service.response.ArticleReadResponse;
import kube.board.common.event.Event;
import kube.board.common.event.EventPayload;
import lombok.RequiredArgsConstructor;
import lombok.extern.slf4j.Slf4j;
import org.springframework.stereotype.Service;

import java.time.Duration;
import java.util.List;
import java.util.Map;
import java.util.Objects;
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
    private final ArticleIdListRepository articleIdListRepository;
    private final BoardArticleCountRepository boardArticleCountRepository;
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

    public ArticleReadPageResponse readAll(Long boardId, Long page, Long pageSize) {
        return ArticleReadPageResponse.of(
                readAll(
                        readAllArticleIds(boardId, page, pageSize)
                ),
                count(boardId)
        );
    }

    private List<ArticleReadResponse> readAll(List<Long> articleIds) {
        Map<Long, ArticleQueryModel> articleQueryModelMap = articleQueryModelRepository.readAll(articleIds);
        return articleIds.stream()
                .map(articleId -> articleQueryModelMap.containsKey(articleId) ?
                        articleQueryModelMap.get(articleId) :
                        fetch(articleId).orElse(null))
                .filter(Objects::nonNull)
                .map(articleQueryModel ->
                        ArticleReadResponse.from(
                articleQueryModel,
                viewClient.count(articleQueryModel.getArticleId())
        ))
                .toList();
    }

    private List<Long> readAllArticleIds(Long boardId, Long page, Long pageSize) {
        List<Long> articleIds = articleIdListRepository.readAll(boardId, (page - 1) * pageSize, pageSize);
        if (pageSize == articleIds.size()){
            log.info("[ArticleReadService.readAllArticleIds] return redis data.");
            return articleIds;
        }
        log.info("[ArticleReadService.readAllArticleIds] return origin data.");
        return articleClient.readAll(boardId, page, pageSize).getArticles().stream()
                .map(ArticleClient.ArticleResponse::getArticleId)
                .toList();
    }

    private long count(Long boardId){
        Long result = boardArticleCountRepository.read(boardId);
        if (result != null) {
            return result;
        }
        long count = articleClient.count(boardId);
        boardArticleCountRepository.createOrUpdate(boardId, count);
        return count;
    }

    public List<ArticleReadResponse> readAllInfiniteScroll(Long boardId, Long lastArticleId, Long pageSize) {
        return readAll(
                readAllInfiniteScrollArticleIds(boardId, lastArticleId, pageSize)
        );
    }

    private List<Long> readAllInfiniteScrollArticleIds(Long boardId, Long lastArticleId, Long pageSize) {
        List<Long> articleIds = articleIdListRepository.readAllInfiniteScroll(boardId, lastArticleId, pageSize);
        if (pageSize == articleIds.size()) {
            log.info("[ArticleReadService.readAllInfiniteScrollArticleIds] return redis data.");
            return articleIds;
        }
        log.info("[ArticleReadService.readAllInfiniteScrollArticleIds] return origin data.");
        return articleClient.readAllInfiniteScroll(boardId, lastArticleId, pageSize).stream()
                .map(ArticleClient.ArticleResponse::getArticleId)
                .toList();
    }


}
