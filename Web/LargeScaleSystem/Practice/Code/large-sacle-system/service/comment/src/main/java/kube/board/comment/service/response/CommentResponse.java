package kube.board.comment.service.response;

import kube.board.comment.entity.Comment;
import kube.board.comment.entity.CommentPath;
import kube.board.comment.entity.CommentV2;
import lombok.Getter;
import lombok.ToString;

import java.time.LocalDateTime;

@Getter
@ToString
public class CommentResponse {
    private Long commentId;
    private String content;
    private Long parentCommentId;
    private String path;
    private Long articleId;
    private Long writerId;
    private Boolean deleted;
    private LocalDateTime createdAt;

    public static CommentResponse from(Comment comment){
        CommentResponse response = new CommentResponse();
        response.commentId = comment.getCommentId();
        response.content = comment.getContent();
        response.parentCommentId = comment.getParentCommentId();
        response.articleId = comment.getArticleId();
        response.writerId = comment.getWriterId();
        response.deleted = comment.getDeleted();
        response.createdAt = comment.getCreatedAt();
        return response;
    }
    public static CommentResponse from(CommentV2 comment){
        CommentResponse response = new CommentResponse();
        response.commentId = comment.getCommentId();
        response.content = comment.getContent();
        response.path = comment.getCommentPath().getPath();
        response.articleId = comment.getArticleId();
        response.writerId = comment.getWriterId();
        response.deleted = comment.getDeleted();
        response.createdAt = comment.getCreatedAt();
        return response;
    }



}
