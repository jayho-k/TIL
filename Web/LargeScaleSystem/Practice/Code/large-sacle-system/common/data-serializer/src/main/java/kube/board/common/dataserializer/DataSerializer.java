package kube.board.common.dataserializer;

import com.fasterxml.jackson.core.JsonProcessingException;
import com.fasterxml.jackson.databind.DeserializationFeature;
import com.fasterxml.jackson.databind.ObjectMapper;
import com.fasterxml.jackson.datatype.jsr310.JavaTimeModule;
import lombok.AccessLevel;
import lombok.NoArgsConstructor;
import lombok.extern.slf4j.Slf4j;

@Slf4j
@NoArgsConstructor(access = AccessLevel.PROTECTED)
public class DataSerializer {

    // Java 객체를 JSON,XML,CSV 등 형식을 바꿔주는 역할을 한다.
    private static final ObjectMapper objectMapper = initialize();

    private static ObjectMapper initialize() {
        return new ObjectMapper()
                .registerModule(new JavaTimeModule()) // 시간 관련된 직렬화를 처리하기 위함
                .configure(DeserializationFeature.FAIL_ON_UNKNOWN_PROPERTIES, false);
    }

    public static <T> T deserialize(String data, Class<T> clazz){
        try {
            return objectMapper.readValue(data, clazz);
        } catch (JsonProcessingException e) {
            log.error("[Deserializer.deserializer] data={}, clazz{}", data, clazz, e);
        }
        return null;
    }

    public static <T> T deserialize(Object data, Class<T> clazz){
        return objectMapper.convertValue(data, clazz);
    }

    public static String serialize(Object object){
        try {
            return objectMapper.writeValueAsString(object);
        }catch (JsonProcessingException e){
            log.error("[Deserializer.deserializer] object={}", object, object);
            return null;
        }

    }

}
