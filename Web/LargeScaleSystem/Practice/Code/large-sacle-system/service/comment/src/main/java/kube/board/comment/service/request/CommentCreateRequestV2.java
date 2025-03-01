package kube.board.comment.service.request;

import kube.board.comment.entity.CommentPath;
import lombok.AllArgsConstructor;
import lombok.Getter;

@Getter
@AllArgsConstructor
public class CommentCreateRequestV2 {
    private Long articleId;
    private String content;
    private String parentPath;
    private Long writerId;

}
