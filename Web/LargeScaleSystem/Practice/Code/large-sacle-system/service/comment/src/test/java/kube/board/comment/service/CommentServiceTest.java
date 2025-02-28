package kube.board.comment.service;

import kube.board.comment.entity.Comment;
import kube.board.comment.repository.CommentRepository;
import org.junit.jupiter.api.DisplayName;
import org.junit.jupiter.api.Test;
import org.junit.jupiter.api.extension.ExtendWith;
import org.mockito.InjectMocks;
import org.mockito.Mock;
import org.mockito.junit.jupiter.MockitoExtension;


import java.util.Optional;

import static org.mockito.BDDMockito.given;
import static org.mockito.Mockito.*;

@ExtendWith(MockitoExtension.class)
class CommentServiceTest {

    @InjectMocks
    CommentService commentService;
    @Mock
    CommentRepository commentRepository;

    @Test
    @DisplayName("삭제할 댓글이 자식 있으면, 삭제 표시만 한다.")
    void deleteShouldMarkDeletedIfHasChildren(){
        // given
        Long articleId = 1L;
        Long commentId = 2L;
        Comment comment = createComment(articleId, commentId);
        given(commentRepository.findById(commentId))
                .willReturn(Optional.of(comment));
        given(commentRepository.countBy(articleId, commentId, 2L)).willReturn(2L);

        // when
        commentService.delete(commentId);

        // then
        verify(comment).delete();
    }

    private Comment createComment(Long articleId, Long commentId) {
        Comment comment = mock(Comment.class);
        given(comment.getArticleId()).willReturn(articleId);
        given(comment.getCommentId()).willReturn(commentId);
        return comment;
    }

    private Comment createComment(Long articleId, Long commentId, Long parentCommentId) {
        Comment comment = createComment(articleId, commentId);
        given(comment.getParentCommentId()).willReturn(parentCommentId);
        return comment;
    }

    @Test
    @DisplayName("하위 댓글이 삭제 되고, 삭제되지 않은 부모면, 하위 댓글만 삭제")
    void deleteShouldDeleteChildOnlyIfNoDeletedParent(){
        // given
        Long articleId = 1L;
        Long commentId = 2L;
        Long parentCommentId = 1L;

        Comment comment = createComment(articleId, commentId, parentCommentId);
        given(comment.isRoot()).willReturn(false);

        Comment parentComment = mock(Comment.class);

        given(parentComment.getDeleted()).willReturn(false);

        given(commentRepository.findById(commentId))
                .willReturn(Optional.of(comment));

        given(commentRepository.countBy(articleId, commentId, 2L))
                .willReturn(1L);

        given(commentRepository.findById(parentCommentId))
                .willReturn(Optional.of(parentComment)); // 상위 댓글을 찾아오는 경우

        // when
        commentService.delete(commentId);

        // then
        verify(commentRepository).delete(comment); // 해당 댓글은 삭제
        verify(commentRepository, never()).delete(parentComment); // 부모는 삭제 x
    }
    @Test
    @DisplayName("하위 댓글이 삭제 되고, 삭제된 부모면, 재귀적으로 모두 삭제한다.")
    void deleteShouldDeleteChildOnlyIfDeletedParent(){
        // given
        Long articleId = 1L;
        Long commentId = 2L;
        Long parentCommentId = 1L;

        // 자식 댓글
        Comment comment = createComment(articleId, commentId, parentCommentId);
        given(comment.isRoot()).willReturn(false);

        // 부모 댓글
        Comment parentComment = createComment(articleId, parentCommentId);
        given(parentComment.isRoot()).willReturn(true);
        given(parentComment.getDeleted()).willReturn(true);

        given(commentRepository.findById(commentId))
                .willReturn(Optional.of(comment));

        given(commentRepository.countBy(articleId, commentId, 2L))
                .willReturn(1L);

        given(commentRepository.findById(parentCommentId))
                .willReturn(Optional.of(parentComment)); // 상위 댓글을 찾아오는 경우

        given(commentRepository.countBy(articleId, parentCommentId, 2L))
                .willReturn(1L);

        // when
        commentService.delete(commentId);

        // then
        verify(commentRepository).delete(comment); // 해당 댓글 삭제
        verify(commentRepository).delete(parentComment); // 부모 댓글 삭제
    }
}