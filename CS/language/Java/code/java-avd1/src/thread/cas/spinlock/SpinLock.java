package thread.cas.spinlock;

import java.util.concurrent.atomic.AtomicBoolean;

import static util.MyLogger.log;
import static util.ThreadUtils.sleep;

public class SpinLock {

    private final AtomicBoolean lock = new AtomicBoolean(false);

    public void lock(){
        log("lock acquired");
        while (!lock.compareAndSet(false, true)){
            log("lock 획득 실패 - 스핀 대기");
        }
        log("lock 획득 성공");
    }

    public void unlock(){
        lock.set(false);
        log("lock return complete");
    }

}
