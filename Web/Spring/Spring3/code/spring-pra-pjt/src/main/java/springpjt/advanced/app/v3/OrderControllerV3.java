package springpjt.advanced.app.v3;

import lombok.RequiredArgsConstructor;
import org.springframework.web.bind.annotation.GetMapping;
import org.springframework.web.bind.annotation.RestController;
import springpjt.advanced.trace.TraceStatus;
import springpjt.advanced.trace.hellotrace.HelloTraceV2;
import springpjt.advanced.trace.logtrace.FieldLogTrace;
import springpjt.advanced.trace.logtrace.LogTrace;

@RestController // @Controller + @ResponseBody
@RequiredArgsConstructor
public class OrderControllerV3 {
    private final OrderServiceV3 orderServiceV3;
    private final LogTrace trace;

    @GetMapping("/v3/request")
    public String request(String itemId){

        // 예외가 터졌을 때 호출이 안되기 때문에 try, catch해줘야함
        TraceStatus status = null;
        try{
            status = trace.begin("OrderController.request");
            orderServiceV3.orderItem(itemId);
            trace.end(status);
            return "ok";
        }catch (Exception e){
            trace.exception(status, e);
            throw e; // 예외를 꼭 다시 던져줘야한다.
        }
    }
}
