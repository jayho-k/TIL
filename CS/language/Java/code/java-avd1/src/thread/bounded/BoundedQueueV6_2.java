package thread.bounded;

import java.util.concurrent.ArrayBlockingQueue;
import java.util.concurrent.BlockingQueue;

public class BoundedQueueV6_1 implements BoundedQueue{

    private BlockingQueue<String> queue;

    public BoundedQueueV6_1(int max){
        this.queue = new ArrayBlockingQueue<>(max);
    }

    @Override
    public void put(String data) throws InterruptedException {
        queue.put(data);
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
