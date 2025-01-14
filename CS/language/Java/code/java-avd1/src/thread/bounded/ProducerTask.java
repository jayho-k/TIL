package thread.bounded;

import static util.MyLogger.log;

public class ProducerTask implements Runnable{

    private final BoundedQueue queue;
    private final String request;

    public ProducerTask(BoundedQueue queue, String request) {
        this.queue = queue;
        this.request = request;
    }

    @Override
    public void run() {

        log("[생산 시도] " + request + " -> " + queue);
        try {
            queue.put(request);
        } catch (InterruptedException e) {
            throw new RuntimeException(e);
        }
        log("[생산 완료] " + request + " -> " + queue);

    }
}
