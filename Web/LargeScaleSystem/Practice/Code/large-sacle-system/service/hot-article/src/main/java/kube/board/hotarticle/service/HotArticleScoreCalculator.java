package kube.board.hotarticle.service;

import kube.board.common.event.payload.ArticleLikedEventPayload;
import kube.board.hotarticle.repository.ArticleCommentCountRepository;
import kube.board.hotarticle.repository.ArticleLikeCountRepository;
import kube.board.hotarticle.repository.ArticleViewCountRepository;
import lombok.RequiredArgsConstructor;
import org.springframework.stereotype.Component;

@Component
@RequiredArgsConstructor
public class HotArticleScoreCalculator {

    private final ArticleLikeCountRepository articleLikeCountRepository;
    private final ArticleViewCountRepository articleViewCountRepository;
    private final ArticleCommentCountRepository articleCommentCountRepository;

    private static final long ARTICLE_LIKE_COUNT_WEIGHT = 3;
    private static final long ARTICLE_COMMENT_COUNT_WEIGHT = 2;
    private static final long ARTICLE_VIEW_COUNT_WEIGHT = 1;

    public long calculate(Long articleId){
        Long articleLikeCount = articleLikeCountRepository.read(articleId);
        Long articleViewCount = articleViewCountRepository.read(articleId);
        Long articleCommentCount = articleCommentCountRepository.read(articleId);

        return articleLikeCount * ARTICLE_LIKE_COUNT_WEIGHT
                + articleViewCount * ARTICLE_VIEW_COUNT_WEIGHT
                + articleCommentCount * ARTICLE_COMMENT_COUNT_WEIGHT;
    }


}
