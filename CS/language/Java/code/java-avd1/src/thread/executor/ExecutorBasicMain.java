package thread.executor;

import java.util.concurrent.ExecutorService;
import java.util.concurrent.LinkedBlockingQueue;
import java.util.concurrent.ThreadPoolExecutor;
import java.util.concurrent.TimeUnit;

import static thread.executor.ExecutorUtil.*;
import static util.MyLogger.log;
import static util.ThreadUtils.sleep;

public class ExecutorBasicMain {

    public static void main(String[] args) {
        ExecutorService es = new ThreadPoolExecutor(2, 2, 0, TimeUnit.MILLISECONDS, new LinkedBlockingQueue<>());
        log("== 초기 상태 ==");
        printState(es);
        es.execute(new RunnableTask("taskA"));
        es.execute(new RunnableTask("taskB"));
        es.execute(new RunnableTask("taskC")); // 2개까진 만들고 있는걸 재사용해서 사용한다.
        es.execute(new RunnableTask("taskD"));

        log("== 작업 수행 중 ==");
        printState(es);

        sleep(3000);

        log("== 작업 수행 완료 ==");
        printState(es);

        es.shutdown();
        log("== shutdown ==");
        printState(es);
    }

}
