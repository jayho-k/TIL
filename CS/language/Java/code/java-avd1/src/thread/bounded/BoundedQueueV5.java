package thread.bounded;

import java.util.ArrayDeque;
import java.util.Queue;
import java.util.concurrent.locks.Condition;
import java.util.concurrent.locks.Lock;
import java.util.concurrent.locks.ReentrantLock;

import static util.MyLogger.log;

public class BoundedQueueV5 implements BoundedQueue{

    private final Lock lock = new ReentrantLock();
    private final Condition producerCond = lock.newCondition(); // 락은 묶여서 돌아가는 것
    private final Condition consumerCond = lock.newCondition(); // 락은 묶여서 돌아가는 것 = 즉 lock 은 1개 대기 공간은 2개
    private final Queue<String> queue = new ArrayDeque<>();
    public final int max;

    public BoundedQueueV5(int max) {
        this.max = max;
    }

    @Override
    public void put(String data) {

        lock.lock();
        try{
            while (queue.size() == max){
                log("[put] 큐가 가득 참, producerCond.await();");
                try {
                    producerCond.await();
                    log("[put] 생산자 깨어남");
                } catch (InterruptedException e) {
                    throw new RuntimeException(e);
                }
            }
            queue.offer(data);
            log("[put] 생산자 데이터 저장, consumerCond.signal()");
            consumerCond.signal();
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
                log("[take] 큐가 비어있음, consumerCond.await()");
                try {
                    consumerCond.await();
                    log("[take] 소비자 꺠어남");
                } catch (InterruptedException e) {
                    throw new RuntimeException(e);
                }
            }
            String data = queue.poll();
            log("[take] 소비자 데이터 획득, producerCond.signal() 호출");
            producerCond.signal();
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
