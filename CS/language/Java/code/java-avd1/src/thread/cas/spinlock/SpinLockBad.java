package thread.cas.spinlock;

import static util.MyLogger.log;
import static util.ThreadUtils.sleep;

public class SpinLockBad {

    private volatile boolean lock = false;

    public void lock(){
        log("lock acquired");
        while(true){
            if (!lock) { // 1. 락 사용여부 확인
                sleep(100); // 문제 상황 확인용
                lock = true; // 2. 락 값 변경
                break;
            }else {
                // 락을 획득할 때 까지 스핀 대기
                log("acquire fail - spin");
            }
            log("lock acquire complete");
        }
    }

    public void unlock(){
        lock = false;
        log("lock return complete");
    }

}
