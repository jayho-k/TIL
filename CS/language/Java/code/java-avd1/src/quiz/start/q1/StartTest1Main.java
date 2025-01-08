package quiz.start.q1;

import static util.MyLogger.log;

public class StartTest1Main {

    public static void main(String[] args) {
        log("main() start");

        CounterThread runnable = new CounterThread();
        Thread thread = new Thread(runnable);
        thread.start();

        log("main() end");

    }

    static class CounterThread implements Runnable{
        @Override
        public void run() {
            for (int i = 0; i<5; i++){
                log(i+1);
                try {
                    Thread.sleep(1000);
                } catch (InterruptedException e) {
                    throw new RuntimeException(e);
                }
            }
        }
    }
}
