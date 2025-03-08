package kube.board.common.event.payload;

import kube.board.common.event.EventPayload;
import lombok.AllArgsConstructor;
import lombok.Builder;
import lombok.Getter;
import lombok.NoArgsConstructor;

@Getter
@Builder
@NoArgsConstructor
@AllArgsConstructor
public class ArticleViewedEventPayload implements EventPayload {

    private Long articleId;
    private Long articleViewCount;

}
