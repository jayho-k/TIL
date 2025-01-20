package thread.bounded;

public interface BoundedQueue {

    void put(String data) throws InterruptedException;

    String take() throws InterruptedException;

}
