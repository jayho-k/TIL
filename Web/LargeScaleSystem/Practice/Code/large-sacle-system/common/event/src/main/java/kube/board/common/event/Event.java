package kube.board.common.event;


import kube.board.common.dataserializer.DataSerializer;
import lombok.Getter;

// Event 통신을 위한 Class
// event를 kafka로 통신할 때 JSON으로 진행 함
@Getter
public class Event<T extends EventPayload> {

    private Long eventId;
    private EventType type;
    private T payload;

    public static Event<EventPayload> of(Long eventId, EventType type, EventPayload payload){
        Event<EventPayload> event = new Event<>();
        event.eventId = eventId;
        event.type = type;
        event.payload = payload;
        return event;
    }

    public String toJson(){
        return DataSerializer.serialize(this);
    }

    public static Event<EventPayload> fromJson(String json){
        EventRaw eventRaw = DataSerializer.deserialize(json, EventRaw.class);
        if (eventRaw == null){
            return null;
        }
        Event<EventPayload> event = new Event<>();
        event.eventId = eventRaw.getEventId();
        event.type = EventType.from(eventRaw.getType());
        event.payload = DataSerializer.deserialize(eventRaw.getPayload(), event.type.getPayloadClass());
        return event;
    }

    @Getter
    private static class EventRaw{
        private Long eventId;
        private String type;
        private Object payload;
    }




}
