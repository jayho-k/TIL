package thread.control;

import static util.MyLogger.log;

public class ThreadStateMain {

    public static void main(String[] args) throws InterruptedException {

        Thread thread = new Thread(
                () -> {

                    try {
                        log("start");
                        log("myThread.state2 = " + Thread.currentThread().getState()); // RUNNABLE
                        log("sleep start");
                        Thread.sleep(3000);
                        log("sleep end");
                        log("myThread.state4 = " + Thread.currentThread().getState()); // RUNNABLE
                        log("end");
                    } catch (InterruptedException e) {
                        throw new RuntimeException(e);
                    }
                });


        log("myThread.state1 = " + thread.getState()); // NEW
        log("myThread.start()");
        thread.start();
        Thread.sleep(1000);
        log("myThread.state3 = " + thread.getState()); // TIMED_WAITING
        Thread.sleep(4000);
        log("myThread.state5 = " + thread.getState()); // TERMINATED

    }

}
