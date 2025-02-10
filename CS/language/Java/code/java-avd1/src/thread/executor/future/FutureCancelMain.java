package thread.executor.future;

import java.util.concurrent.*;

import static util.MyLogger.log;
import static util.ThreadUtils.sleep;

public class FutureCancelMain {

//    private static boolean mayInterruptIfRunning = true;
    private static boolean mayInterruptIfRunning = false;

    public static void main(String[] args) {
        ExecutorService es = Executors.newFixedThreadPool(1);
        Future<String> future = es.submit(new MyTask());

        sleep(3000);


        // 일정시간 후 취소 시도
        log("future.cancel(" + mayInterruptIfRunning  + ") 호출");
        boolean result = future.cancel(mayInterruptIfRunning);
        log("cancel(" + mayInterruptIfRunning  + ") result : " + result);
        try {
            log("Future result: " + future.get());
        }
        catch (CancellationException e) { // 런타임 예외
            log("Future는 이미 취소 되었습니다.");
        }
        catch (InterruptedException | ExecutionException e) {
            e.printStackTrace();
        }

        // Executor 종료
        es.shutdown();
    }

    static class MyTask implements Callable<String> {

        @Override
        public String call() throws Exception {
            try{
                for (int i=0;i<10;i++){
                    log("작업 중 : " + i);
                    Thread.sleep(1000);
                }
            }catch (InterruptedException e){
                log("인터럽트 발생");
                return "interrupted";
            }
            return "Complete";
        }

    }

}
