package thread.executor.future;

import java.util.concurrent.*;

import static util.MyLogger.log;
import static util.ThreadUtils.sleep;

public class FutureExceptionMain {

    public static void main(String[] args) {
        ExecutorService es = Executors.newFixedThreadPool(1);
        log("작업 전달");

        Future<Integer> future = es.submit(new ExCallable());
        sleep(1000);

        log("future.get() 호출 시도");

        try{
            Integer result = future.get();

        } catch (ExecutionException e) {
            log("e = " + e);
            Throwable cause = e.getCause();
            log("cause = " + cause); // 원본 예외
        } catch (InterruptedException e) {
            throw new RuntimeException(e);
        }
        es.shutdown();
    }

    static class ExCallable implements Callable<Integer>{

        @Override
        public Integer call() throws Exception {
            log("Callable 실행, 예외 발생");
            throw new IllegalStateException("ex");
        }
    }
}
