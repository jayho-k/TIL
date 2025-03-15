package kube.board.articleread.service;

import kube.board.articleread.repository.ArticleQueryModel;

import java.time.LocalDateTime;

public class ArticleReadResponse {

    private Long articleId;
    private String title;
    private String content;
    private Long boardId;
    private Long writerId;
    private LocalDateTime createdAt;
    private LocalDateTime modifiedAt;
    private Long articleCommentCount;
    private Long articleLikeCount;
    private Long articleViewCount; // 쓰기 Traffic 또한 있기 때문에 직접 가져올 것

    public static ArticleReadResponse from(ArticleQueryModel articleQueryModel, Long viewCount){
        ArticleReadResponse response = new ArticleReadResponse();
        response.articleId = articleQueryModel.getArticleId();
        response.title = articleQueryModel.getTitle();
        response.content = articleQueryModel.getContent();
        response.boardId = articleQueryModel.getBoardId();
        response.writerId = articleQueryModel.getWriterId();
        response.createdAt = articleQueryModel.getCreatedAt();
        response.modifiedAt = articleQueryModel.getModifiedAt();
        response.articleCommentCount = articleQueryModel.getArticleCommentCount();
        response.articleLikeCount = articleQueryModel.getArticleLikeCount();
        response.articleViewCount = viewCount;
        return response;
    }

}
