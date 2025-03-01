package kube.board.comment.entity;

import jakarta.persistence.Embedded;
import jakarta.persistence.Entity;
import jakarta.persistence.Id;
import jakarta.persistence.Table;
import lombok.AccessLevel;
import lombok.Getter;
import lombok.NoArgsConstructor;
import lombok.ToString;

import java.time.LocalDateTime;

@Table(name = "comment_v2")
@Getter
@Entity
@ToString
@NoArgsConstructor(access = AccessLevel.PROTECTED)
public class CommentV2 {

    @Id
    private Long commentId;
    private String content;
    @Embedded
    private CommentPath commentPath;
    private Long articleId;
    private Long writerId;
    private Boolean deleted;
    private LocalDateTime createdAt;

    public static CommentV2 create(Long commentId, String content, Long articleId, Long writerId, CommentPath commentPath){
        CommentV2 commentV2 = new CommentV2();
        commentV2.commentId = commentId;
        commentV2.content = content;
        commentV2.commentPath = commentPath;
        commentV2.articleId = articleId;
        commentV2.writerId = writerId;
        commentV2.deleted = false;
        commentV2.createdAt = LocalDateTime.now();
        return commentV2;
    }

    public boolean isRoot(){
        return commentPath.isRoot();
    }

    // delete 여부
    public void delete(){
        deleted = true;
    }




}

