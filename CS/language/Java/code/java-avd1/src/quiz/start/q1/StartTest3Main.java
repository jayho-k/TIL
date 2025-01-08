package quiz.start.q1;

import static util.MyLogger.log;

public class StartTest3Main {

    public static void main(String[] args) {
        log("main() start");

        Thread thread = new Thread(new Runnable() {
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
        });
        thread.start();

        log("main() end");

    }
}
