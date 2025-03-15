package kube.board.articleread.service.event.hadler;

import kube.board.common.event.Event;
import kube.board.common.event.EventPayload;

public interface EventHandler<T extends EventPayload> {
    void handler(Event<T> event);
    boolean supports(Event<T> event);
}
