package kube.board.comment.service;

import kube.board.comment.entity.Comment;
import kube.board.comment.repository.CommentRepository;
import kube.board.comment.service.request.CommentCreateRequest;
import kube.board.comment.service.response.CommentPageResponse;
import kube.board.comment.service.response.CommentResponse;
import kube.board.common.snowflake.Snowflake;
import lombok.RequiredArgsConstructor;
import org.springframework.stereotype.Service;
import org.springframework.transaction.annotation.Transactional;

import java.util.List;
import java.util.Optional;

import static java.util.function.Predicate.not;

@Service
@RequiredArgsConstructor
public class CommentService {

    private final Snowflake snowflake = new Snowflake();
    private final CommentRepository commentRepository;

    @Transactional
    public CommentResponse create(CommentCreateRequest request){
        Comment parent = findParent(request);
        Comment comment = commentRepository.save(
                Comment.create(
                        snowflake.nextId(),
                        request.getContent(),
                        parent == null ? null : parent.getCommentId(),
                        request.getArticleId(),
                        request.getWriterId()
                )
        );
        return CommentResponse.from(comment);
    }

    private Comment findParent(CommentCreateRequest request) {
        Long parentCommentId = request.getParentCommentId();

        // 새로운 댓글
        if (parentCommentId == null) {
            return null;
        }
        // 대댓글
        return commentRepository.findById(parentCommentId)
                .filter(not(Comment::getDeleted)) // 삭제 여부 확인
                .filter(Comment::isRoot) // root 인지 확인
                .orElseThrow();
    }

    public CommentResponse read(Long commentId) {
        return CommentResponse.from(
                commentRepository.findById(commentId).orElseThrow()
        );
    }

    @Transactional
    public void delete(Long commentId){
        commentRepository.findById(commentId)
                .filter(not(Comment::getDeleted)) // 삭제 되어있으면 안됨
                .ifPresent(comment -> {
                    if (hasChildren(comment)) {
                        comment.delete();
                    } else {
                        delete(comment);
                    }
                });
    }

    private boolean hasChildren(Comment comment) {
        // child 가 존재하는지만 판단.
        // 자기 자신 + child 중 하나
        return commentRepository.countBy(comment.getArticleId(), comment.getCommentId(), 2L) == 2;
    }

    private void delete(Comment comment) {
        // 삭제
        commentRepository.delete(comment);

        // 자신이 root 가 아니라면 부모 comment 들 delete
        if (!comment.isRoot()){
            commentRepository.findById(comment.getParentCommentId())
                    .filter(Comment::getDeleted) // 삭제가 되어있으면 안되고,
                    .filter(not(this::hasChildren)) // 자식을 가지고 있으면 안되고,
                    .ifPresent(this::delete); // 상위 댓글 삭제
        }
    }

    public CommentPageResponse readAll(Long articleId, Long page, Long pageSize) {
        return CommentPageResponse.of(
                commentRepository.findAll(articleId, (page - 1) * pageSize, pageSize).stream()
                        .map(CommentResponse::from)
                        .toList(),
                commentRepository.count(articleId, PageLimitCalculator.calculatePageLimit(page, pageSize, 10L))
        );
    }

    public List<CommentResponse> readAll(Long articleId, Long lastParentCommentId, Long lastCommentId, Long limit) {
        List<Comment> comments = lastParentCommentId == null || lastCommentId == null ?
                commentRepository.findAllInfiniteScroll(articleId, limit) :
                commentRepository.findAllInfiniteScroll(articleId, lastParentCommentId, lastCommentId, limit);

        return comments.stream()
                .map(CommentResponse::from)
                .toList();
    }



}
