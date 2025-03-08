package kube.board.common.event;

import kube.board.common.event.payload.*;
import lombok.Getter;
import lombok.RequiredArgsConstructor;
import lombok.extern.slf4j.Slf4j;

@Slf4j
@Getter
@RequiredArgsConstructor
public enum EventType {

    ARTICLE_CREATED(ArticleCreatedEventPayload.class, Topic.LARGE_SCALE_SYSTEM_ARTICLE),
    ARTICLE_UPDATED(ArticleUpdatedEventPayload.class, Topic.LARGE_SCALE_SYSTEM_ARTICLE),
    ARTICLE_DELETED(ArticleDeletedEventPayload.class, Topic.LARGE_SCALE_SYSTEM_ARTICLE),
    COMMENT_CREATED(CommentCreatedEventPayload.class, Topic.LARGE_SCALE_SYSTEM_COMMENT),
    COMMENT_DELETED(CommentDeletedEventPayload.class, Topic.LARGE_SCALE_SYSTEM_COMMENT),
    ARTICLE_LIKE(ArticleLikedEventPayload.class, Topic.LARGE_SCALE_SYSTEM_LIKE),
    ARTICLE_UNLIKED(ArticleUnlikedEventPayload.class, Topic.LARGE_SCALE_SYSTEM_LIKE),
    ARTICLE_VIEWED(ArticleViewedEventPayload.class, Topic.LARGE_SCALE_SYSTEM_VIEW)
    ;

    private final Class<? extends EventPayload> payloadClass;
    private final String topic;

    public static EventType from(String type){
        try{
            return valueOf(type);
        }catch (Exception e){
            log.error("[EventType.from] type={}", type, e);
            return null;
        }
    }

    public static class Topic{
        public static final String LARGE_SCALE_SYSTEM_ARTICLE = "large-scale-system-article";
        public static final String LARGE_SCALE_SYSTEM_COMMENT = "large-scale-system-comment";
        public static final String LARGE_SCALE_SYSTEM_LIKE = "large-scale-system-like";
        public static final String LARGE_SCALE_SYSTEM_VIEW = "large-scale-system-view";
    }




}
