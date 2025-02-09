package thread.executor.future;

import java.util.Random;
import java.util.concurrent.*;

import static util.MyLogger.log;
import static util.ThreadUtils.sleep;

public class CallableMainV1 {
    public static void main(String[] args) throws ExecutionException, InterruptedException {
        // Pool 하나만 있는 Util
        ExecutorService es = Executors.newFixedThreadPool(1);
        Future<Integer> future = es.submit(new MyCallable());
        Integer res = future.get();
        log("res : " + res);
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
