package thread.bounded;

import java.util.concurrent.ArrayBlockingQueue;
import java.util.concurrent.BlockingQueue;

import static util.MyLogger.log;

public class BoundedQueueV6_2 implements BoundedQueue{

    private BlockingQueue<String> queue;

    public BoundedQueueV6_2(int max){
        this.queue = new ArrayBlockingQueue<>(max);
    }

    @Override
    public void put(String data) throws InterruptedException {
        log("저장 시도 결과 = " + queue.offer(data));
    }

    @Override
    public String take() throws InterruptedException {
        return queue.take();
    }

    @Override
    public String toString() {
        return queue.toString();
    }
}
