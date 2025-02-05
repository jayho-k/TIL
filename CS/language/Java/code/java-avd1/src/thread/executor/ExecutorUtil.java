package thread.executor;

import java.util.concurrent.ExecutorService;
import java.util.concurrent.ThreadPoolExecutor;

import static util.MyLogger.log;

public class ExecutorUtil {

    public static void printState(ExecutorService executorService){

        // ThreadPoolExecutor abc = (ThreadPoolExecutor) executorService; 아래는 이거와 같은 것
        if (executorService instanceof ThreadPoolExecutor poolExecutor){
            int poolSize = poolExecutor.getPoolSize();
            int activeCount = poolExecutor.getActiveCount();
            int queued = poolExecutor.getQueue().size();
            long completedTaskCount = poolExecutor.getCompletedTaskCount();
            log("[pool=" + poolSize + ", active=" + activeCount + ", queueTasks=" + queued + ", completedTask" + completedTaskCount);

        }
        else{
            log(executorService);
        }
    }

}
