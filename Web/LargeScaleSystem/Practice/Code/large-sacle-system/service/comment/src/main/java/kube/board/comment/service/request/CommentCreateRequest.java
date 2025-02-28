package kube.board.comment.service.request;

import lombok.Getter;

import java.time.LocalDateTime;

@Getter
public class CommentCreateRequest {
    private Long articleId;
    private String content;
    private Long parentCommentId;
    private Long writerId;

}
