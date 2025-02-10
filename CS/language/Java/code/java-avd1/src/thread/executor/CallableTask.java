package thread.executor;

import java.util.concurrent.Callable;

import static util.MyLogger.log;
import static util.ThreadUtils.sleep;

public class CallableTask implements Callable<Integer> {

    String name;
    int sleepMs;

    public CallableTask(String name, int sleepMs){
        this.name = name;
        this.sleepMs = sleepMs;
    }

    @Override
    public Integer call() throws Exception {

        log(name + " 실행");
        sleep(sleepMs);
        log(name + " 완료");

        return sleepMs;
    }
}
