package thread.bounded;

import static util.MyLogger.log;

public class ConsumerTask implements Runnable{

    private BoundedQueue queue;
    private BoundedQueue queueTest;

    public ConsumerTask(BoundedQueue queue){
        this.queue = queue;
    }

    @Override
    public void run() {
        log("[소비 시도] ?  <-  " + queue);
        String data = queue.take();
        log("[소비 시도] ? "+ data + " <-  " + queue);


    }
}
