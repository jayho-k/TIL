package thread.executor.future;

import java.util.Random;
import java.util.concurrent.*;

import static util.MyLogger.log;
import static util.ThreadUtils.sleep;

public class CallableMainV2 {
    public static void main(String[] args) throws ExecutionException, InterruptedException {
        // Pool 하나만 있는 Util
        ExecutorService es = Executors.newFixedThreadPool(1);
        log("submit() 호출");
        Future<Integer> future = es.submit(new MyCallable());
        log("submit() 반환, future" + future);

        log("future.get() [blocking] 메서드 호출 시작 -> main 스레드 waiting");
        Integer res = future.get();
        log("future.get() [blocking] 메서드 호출 완료 -> main 스레드 runnable");
        log("res : " + res);
        log("future 완료, future" + future);

        es.shutdown();
    }

    static class MyCallable implements Callable<Integer>{

        @Override
        public Integer call() throws Exception {
            log("Callable 시작 ");
            sleep(2000);
            int value = new Random().nextInt(10);
            log("value : " + value);
            log("Callable 완료 ");
            return value;
        }
    }
}
