package thread.bounded;

import java.util.concurrent.ArrayBlockingQueue;
import java.util.concurrent.BlockingQueue;
import java.util.concurrent.TimeUnit;

import static util.MyLogger.log;

public class BoundedQueueV6_3 implements BoundedQueue{

    private BlockingQueue<String> queue;

    public BoundedQueueV6_3(int max){
        this.queue = new ArrayBlockingQueue<>(max);
    }

    @Override
    public void put(String data) throws InterruptedException {

        queue.offer(data,1, TimeUnit.MILLISECONDS);
    }

    @Override
    public String take() throws InterruptedException {
        return queue.poll(2, TimeUnit.SECONDS);
    }

    @Override
    public String toString() {
        return queue.toString();
    }
}
