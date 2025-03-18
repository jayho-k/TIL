package springpjt.advanced.app.v3;

import lombok.RequiredArgsConstructor;
import org.springframework.stereotype.Repository;
import springpjt.advanced.trace.TraceId;
import springpjt.advanced.trace.TraceStatus;
import springpjt.advanced.trace.hellotrace.HelloTraceV2;
import springpjt.advanced.trace.logtrace.FieldLogTrace;
import springpjt.advanced.trace.logtrace.LogTrace;

@Repository
@RequiredArgsConstructor
public class OrderRepositoryV3 {

    private final LogTrace trace;

    public void save(String itemId){

        // 예외가 터졌을 때 호출이 안되기 때문에 try, catch 해줘야함
        TraceStatus status = null;
        try{
            status = trace.begin("OrderRepository.save");

            // 상품 ID가 ex로 넘어오면 exception 터뜨려라
            if (itemId.equals("ex")){
                throw new IllegalStateException("Exception");
            }
            sleep(1000); //주문하는데 1초정도 걸린다고 가정
            trace.end(status);

        }catch (Exception e){
            trace.exception(status, e);
            throw e; // 예외를 꼭 다시 던져줘야한다.
        }
    }

    private void sleep(int millis) {
        try{
            Thread.sleep(millis);
        } catch (InterruptedException e){
            e.printStackTrace();
        }
    }
}
