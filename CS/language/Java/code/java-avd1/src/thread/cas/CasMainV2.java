package thread.cas;

import java.util.concurrent.atomic.AtomicInteger;

import static util.MyLogger.log;

public class CasMainV2 {

    public static void main(String[] args) {
        AtomicInteger atomicInteger = new AtomicInteger(0);
        System.out.println("start value = " + atomicInteger.get());

        // incrementAndGet 구현
        int resultValue1 = incrementAndGet(atomicInteger);

        int resultValue2 = incrementAndGet(atomicInteger);

    }

    private static int incrementAndGet(AtomicInteger atomicInteger) {
        int getValue;
        boolean result;

        do{
            getValue = atomicInteger.get(); // thread1 : 0
            log("getValue : " + getValue);

            // 중간에 thread2 : value->1로 이미 만든 상태?
            // compareAndSet 부분에서 False가 나올 것임
            // 그럼 while문을 다시 돌린다. => 즉 최신 업데이트 부터 보는 것

            // 아무도 바꾸지 않았을 경우에만 값을 바꾸겠다는 뜻이다.
            result = atomicInteger.compareAndSet(getValue, getValue + 1);
            log("result : " + result);
        }while (!result);

        return getValue;
    }

}
