package thread.bounded;

import java.util.ArrayDeque;
import java.util.Queue;
import java.util.concurrent.locks.Condition;
import java.util.concurrent.locks.Lock;
import java.util.concurrent.locks.ReentrantLock;

import static util.MyLogger.log;

public class BoundedQueueV4 implements BoundedQueue{

    private final Lock lock = new ReentrantLock();
    private final Condition condition = lock.newCondition(); // 이렇게 하면 여기가 대기 집합이 된다.
    private final Queue<String> queue = new ArrayDeque<>();
    public final int max;

    public BoundedQueueV4(int max) {
        this.max = max;
    }

    @Override
    public void put(String data) {

        lock.lock();
        try{
            while (queue.size() == max){
                log("[put] 큐가 가득 참, 생산자 대기");
                try {
                    condition.await();
                    log("[put] 생산자 깨어남");
                } catch (InterruptedException e) {
                    throw new RuntimeException(e);
                }
            }
            queue.offer(data);
            log("[put] 생산자 데이터 저장, notify() 호출");
            condition.signal();
        }
        finally {
            lock.unlock();
        }
    }

    @Override
    public String take() {

        lock.lock();
        try{
            while(queue.isEmpty()){
                log("[take] 큐가 비어있음, 소비자 대기");
                try {
                    condition.await();
                    log("[take] 소비자 꺠어남");
                } catch (InterruptedException e) {
                    throw new RuntimeException(e);
                }
            }
            String data = queue.poll();
            log("[take] 소비자 데이터 획득, notify()호출");
            condition.signal();
            return data;
        }finally {
            lock.unlock();
        }
    }


    @Override
    public String toString() {
        return queue.toString();
    }
}
