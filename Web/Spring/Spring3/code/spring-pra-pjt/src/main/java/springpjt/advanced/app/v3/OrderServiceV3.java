package springpjt.advanced.app.v3;

import lombok.RequiredArgsConstructor;
import org.springframework.stereotype.Service;
import springpjt.advanced.trace.TraceId;
import springpjt.advanced.trace.TraceStatus;
import springpjt.advanced.trace.logtrace.LogTrace;

@Service
@RequiredArgsConstructor
public class OrderServiceV3 {
    private final OrderRepositoryV3 orderRepositoryV3;
    private final LogTrace trace;

    public void orderItem(String itemId){
        // 예외가 터졌을 때 호출이 안되기 때문에 try, catch해줘야함
        TraceStatus status = null;
        try{
            status = trace.begin("OrderController.request");
            orderRepositoryV3.save(itemId);
            trace.end(status);
        }catch (Exception e){
            trace.exception(status, e);
            throw e; // 예외를 꼭 다시 던져줘야한다.
        }
    }
}
