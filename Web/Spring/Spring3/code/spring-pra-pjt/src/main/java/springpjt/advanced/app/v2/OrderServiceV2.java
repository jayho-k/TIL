package springpjt.advanced.app.v2;

import lombok.RequiredArgsConstructor;
import org.springframework.stereotype.Service;
import springpjt.advanced.trace.TraceId;
import springpjt.advanced.trace.TraceStatus;
import springpjt.advanced.trace.hellotrace.HelloTraceV2;

@Service
@RequiredArgsConstructor
public class OrderServiceV2 {
    private final OrderRepositoryV2 orderRepositoryV2;
    private final HelloTraceV2 trace;

    public void orderItem(TraceId traceId, String itemId){
        // 예외가 터졌을 때 호출이 안되기 때문에 try, catch해줘야함
        TraceStatus status = null;
        try{
            status = trace.beginSync(traceId,"OrderController.request");
            orderRepositoryV2.save(status.getTraceId(),itemId);
            trace.end(status);
        }catch (Exception e){
            trace.exception(status, e);
            throw e; // 예외를 꼭 다시 던져줘야한다.
        }
    }
}
