package kube.board.hotarticle.service.eventhandler;

import kube.board.common.event.Event;
import kube.board.common.event.EventPayload;

public interface EventHandler <T extends EventPayload>{

    void handler(Event<T> event); // 처리하는 로직을 정의하는 handle method

    boolean supports(Event<T> event); // event handler가 event를 지원하는지 확인하는 supports method

    Long findArticleId(Event<T> event);

}
