package springpjt.advanced.app.v1;

import lombok.RequiredArgsConstructor;
import org.springframework.stereotype.Service;
import springpjt.advanced.app.v1.OrderRepositoryV1;
import springpjt.advanced.trace.TraceStatus;
import springpjt.advanced.trace.hellotrace.HelloTraceV1;

@Service
@RequiredArgsConstructor
public class OrderServiceV1 {
    private final OrderRepositoryV1 orderRepositoryV1;
    private final HelloTraceV1 trace;

    public void orderItem(String itemId){
        // 예외가 터졌을 때 호출이 안되기 때문에 try, catch해줘야함
        TraceStatus status = null;
        try{
            status = trace.begin("OrderController.request");
            orderRepositoryV1.save(itemId);
        }catch (Exception e){
            trace.exception(status, e);
            throw e; // 예외를 꼭 다시 던져줘야한다.
        }
    }
}
