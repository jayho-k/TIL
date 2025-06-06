package springpjt.advanced.trace.threadllocal;

import lombok.extern.slf4j.Slf4j;
import springpjt.advanced.trace.TraceId;
import springpjt.advanced.trace.TraceStatus;
import springpjt.advanced.trace.logtrace.LogTrace;


@Slf4j
public class ThreadLoacalService implements LogTrace {

    private static final String START_PREFIX = "-->";
    private static final String COMPLETE_PREFIX = "<--";
    private static final String EX_PREFIX = "<X-";

    private TraceId traceIdHolder; // 동시성 이슈가 발생할 수 있음 Thread Local 사용해야할 듯


    @Override
    public TraceStatus begin(String message) {
        syncTraceId();
        TraceId traceId = traceIdHolder;
        Long startTimeMs = System.currentTimeMillis();
        log.info("[{}] {}{}", traceId.getId(), addSpace(START_PREFIX,traceId.getLevel()),message);
        return new TraceStatus(traceId, startTimeMs, message);
    }

    private void syncTraceId(){
        if (traceIdHolder == null) {
            traceIdHolder = new TraceId();
        }
        else{
            traceIdHolder = traceIdHolder.createNextId();
        }
    }

    @Override
    public void end(TraceStatus status) {
        complete(status, null);
    }

    @Override
    public void exception(TraceStatus status, Exception e) {
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
        releaseTraceId();
    }

    private void releaseTraceId(){
        if (traceIdHolder.isFirstLevel()) {
            traceIdHolder = null;
        } else {
            traceIdHolder = traceIdHolder.createPreviousId();
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
