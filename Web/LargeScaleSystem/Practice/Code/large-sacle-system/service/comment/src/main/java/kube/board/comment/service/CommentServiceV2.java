package kube.board.comment.service;

import kube.board.comment.entity.ArticleCommentCount;
import kube.board.comment.entity.Comment;
import kube.board.comment.entity.CommentPath;
import kube.board.comment.entity.CommentV2;
import kube.board.comment.repository.ArticleCommentCountRepository;
import kube.board.comment.repository.CommentRepositoryV2;
import kube.board.comment.service.request.CommentCreateRequestV2;
import kube.board.comment.service.response.CommentPageResponse;
import kube.board.comment.service.response.CommentResponse;
import kube.board.common.event.EventType;
import kube.board.common.event.payload.ArticleCreatedEventPayload;
import kube.board.common.event.payload.CommentCreatedEventPayload;
import kube.board.common.event.payload.CommentDeletedEventPayload;
import kube.board.common.outboxmessagerelay.OutboxEventPublisher;
import kube.board.common.snowflake.Snowflake;
import lombok.RequiredArgsConstructor;
import org.springframework.stereotype.Service;
import org.springframework.transaction.annotation.Transactional;

import java.util.List;

import static java.util.function.Predicate.not;

@Service
@RequiredArgsConstructor
public class CommentServiceV2 {

    private final Snowflake snowflake = new Snowflake();
    private final CommentRepositoryV2 commentRepository;
    private final ArticleCommentCountRepository articleCommentCountRepository;
    private final OutboxEventPublisher outboxEventPublisher;

    @Transactional
    public CommentResponse create(CommentCreateRequestV2 request){
        CommentV2 parent = findParent(request);
        CommentPath parentCommentPath = parent == null ? CommentPath.create("") : parent.getCommentPath();
        CommentV2 comment = commentRepository.save(
                CommentV2.create(
                        snowflake.nextId(),
                        request.getContent(),
                        request.getArticleId(),
                        request.getWriterId(),
                        parentCommentPath.createChildCommentPath(
                                commentRepository.findDescendantsTopPath(
                                        request.getArticleId(),
                                        parentCommentPath.getPath()
                                ).orElse(null)
                        )
                )
        );

        int result = articleCommentCountRepository.increase(request.getArticleId());
        if (result == 0){
            articleCommentCountRepository.save(
                    ArticleCommentCount.init(request.getArticleId(), 1L)
            );
        }

        outboxEventPublisher.publish(
                EventType.COMMENT_CREATED,
                CommentCreatedEventPayload.builder()
                        .commentId(comment.getCommentId())
                        .content(comment.getContent())
                        .articleId(comment.getArticleId())
                        .writerId(comment.getWriterId())
                        .deleted(comment.getDeleted())
                        .createdAt(comment.getCreatedAt())
                        .articleCommentCount(count(comment.getArticleId()))
                        .build(),
                comment.getArticleId()
        );


        return CommentResponse.from(comment);
    }

    private CommentV2 findParent(CommentCreateRequestV2 request) {
        String parentPath = request.getParentPath();
        if (parentPath == null) {
            return null;
        }
        return commentRepository.findByPath(parentPath)
                .filter(not(CommentV2::getDeleted))
                .orElseThrow();
    }

    public CommentResponse read(Long commentId){
        return CommentResponse.from(
                commentRepository.findById(commentId).orElseThrow()
        );
    }

    @Transactional
    public void delete(Long commentId){
        commentRepository.findById(commentId)
                .filter(not(CommentV2::getDeleted)) // 삭제가 안된 친구여야 함
                .ifPresent(comment -> {
                    if (hasChildren(comment)){
                        comment.delete();
                    } else {
                        delete(comment);
                    }

                    outboxEventPublisher.publish(
                            EventType.COMMENT_DELETED,
                            CommentDeletedEventPayload.builder()
                                    .commentId(comment.getCommentId())
                                    .content(comment.getContent())
                                    .articleId(comment.getArticleId())
                                    .writerId(comment.getWriterId())
                                    .deleted(comment.getDeleted())
                                    .createdAt(comment.getCreatedAt())
                                    .articleCommentCount(count(comment.getArticleId()))
                                    .build(),
                            comment.getArticleId()
                    );
                });
    }

    private boolean hasChildren(CommentV2 comment) {
        // child 가 있는지 확인 : DescendantsTopPath 가 존재하면 child가 이쓴ㄴ 것
        return commentRepository.findDescendantsTopPath(
                comment.getArticleId(),
                comment.getCommentPath().getPath() // prefix
        ).isPresent();
    }

    private void delete(CommentV2 comment) {
        // 삭제
        commentRepository.delete(comment);
        articleCommentCountRepository.decrease(comment.getArticleId());

        // 자신이 root 가 아니라면 부모 comment 들 delete
        if (!comment.isRoot()){
            commentRepository.findByPath(comment.getCommentPath().getParentPath())
                    .filter(CommentV2::getDeleted) // 삭제가 되어있으면 안되고,
                    .filter(not(this::hasChildren)) // 자식을 가지고 있으면 안되고,
                    .ifPresent(this::delete); // 상위 댓글 삭제
        }



    }

    public CommentPageResponse readAll(Long articleId, Long page, Long pageSize){
        return CommentPageResponse.of(
                commentRepository.findAll(articleId, (page - 1) * pageSize, pageSize).stream()
                        .map(CommentResponse::from)
                        .toList(),
                commentRepository.count(articleId, PageLimitCalculator.calculatePageLimit(page, pageSize, 10L))
        );
    }

    public List<CommentResponse> readAllInfiniteScroll(Long articleId, String lastPath, Long pageSize) {
        List<CommentV2> comments = lastPath == null ?
                commentRepository.findAllInfiniteScroll(articleId, pageSize) :
                commentRepository.findAllInfiniteScroll(articleId, lastPath, pageSize);
        return comments.stream()
                .map(CommentResponse::from)
                .toList();
    }

    public Long count(Long articleId) {
        return articleCommentCountRepository.findById(articleId)
                .map(ArticleCommentCount::getCommentCount)
                .orElse(0L);
    }
}
