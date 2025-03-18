package springpjt.advanced.trace.hellotrace;

import lombok.extern.slf4j.Slf4j;
import org.springframework.stereotype.Component;
import springpjt.advanced.trace.TraceId;
import springpjt.advanced.trace.TraceStatus;

// 싱글톤으로 스프링 빈에 등록해서 사용할 것이다.
// 정상처리 => end
// 에러 => exception
@Slf4j
@Component
public class HelloTraceV2 {
    private static final String START_PREFIX = "-->";
    private static final String COMPLETE_PREFIX = "<--";
    private static final String EX_PREFIX = "<X-";

    public TraceStatus begin(String message){
        TraceId traceId = new TraceId();
        Long startTimeMs = System.currentTimeMillis();
        // addSpace는 화살표 표시를 위한 것
        log.info("[{} {}{}]", traceId.getId(), addSpace(START_PREFIX,traceId.getLevel()),message);
        return new TraceStatus(traceId,startTimeMs,message);
    }

    // trace id는 유지하며 next level로 유지하도록 한다.
    public TraceStatus beginSync(TraceId beforeTraceId, String message){
        TraceId nextId = beforeTraceId.createNextId();
        Long startTimeMs = System.currentTimeMillis();

        // addSpace는 화살표 표시를 위한 것
        log.info("[{} {}{}]", nextId.getId(), addSpace(START_PREFIX,nextId.getLevel()),message);
        return new TraceStatus(nextId,startTimeMs,message);
    }

    public void end(TraceStatus status){
        complete(status, null);
    }
    public void exception(TraceStatus status, Exception e){
        complete(status,e);
    }
    private void complete(TraceStatus status, Exception e){
        Long stopTimeMs = System.currentTimeMillis();
        long resultTimeMs = stopTimeMs - status.getStartTimeMs();
        TraceId traceId = status.getTraceId();

        // 정상작동할 경우
        if (e==null){
            log.info("[{}] {}{} time={}ms", traceId.getId(),
                    addSpace(COMPLETE_PREFIX, traceId.getLevel()), status.getMessage(),
                    resultTimeMs);
        }else{
            // 에러가 터질 경우
            log.info("[{}] {}{} time={}ms ex={}", traceId.getId(),
                    addSpace(EX_PREFIX, traceId.getLevel()), status.getMessage(), resultTimeMs,
                    e.toString());
        }
    }
    private static String addSpace(String prefix, int level){
        StringBuilder sb = new StringBuilder();
        for (int i=0; i<level; i++){
            sb.append((i==level-1) ? "|" + prefix : "|  ");
        }
        return sb.toString();
    }

}
