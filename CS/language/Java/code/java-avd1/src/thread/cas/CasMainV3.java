package thread.cas;

import java.util.ArrayList;
import java.util.List;
import java.util.concurrent.atomic.AtomicInteger;

import static util.MyLogger.log;
import static util.ThreadUtils.sleep;

public class CasMainV3 {

    private static final int THREAD_COUND = 2;
    public static void main(String[] args) throws InterruptedException {
            AtomicInteger atomicInteger = new AtomicInteger(0);
        System.out.println("start value = " + atomicInteger.get());

        Runnable runnable = new Runnable() {
            @Override
            public void run() {
                incrementAndGet(atomicInteger);
            }
        };

        List<Thread> threadList = new ArrayList<>();
        for (int i = 0; i < THREAD_COUND; i++){
            Thread thread = new Thread(runnable);
            threadList.add(thread);
            thread.start();
        }

        for (Thread thread : threadList){
            thread.join();
        }

        int res = atomicInteger.get();
        System.out.println("AtomicInteger resultValue : " + res);
    }


    private static int incrementAndGet(AtomicInteger atomicInteger) {
        int getValue;
        boolean result;

        do{
            getValue = atomicInteger.get(); // thread1 : 0
            sleep(100); // 스레드 동시 실행을 위한 대기
            log("getValue : " + getValue);

            // 중간에 thread2 : value->1로 이미 만든 상태?
            // compareAndSet 부분에서 False가 나올 것임
            // 그럼 while문을 다시 돌린다. => 즉 최신 업데이트 부터 보는 것

            // 아무도 바꾸지 않았을 경우에만 값을 바꾸겠다는 뜻이다.
            result = atomicInteger.compareAndSet(getValue, getValue + 1);
            log("result : " + result);
        }while (!result);

        return getValue+1;
    }

}
