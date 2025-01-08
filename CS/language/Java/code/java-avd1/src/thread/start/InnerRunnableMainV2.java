package thread.start;

import static util.MyLogger.log;

public class InnerRunnableMainV2 {
    public static void main(String[] args) {

        log("main() start");

        // 익명 class : 특정 method 안에서 간단하게 쓸 때
        Runnable runnable = new Runnable() {
            @Override
            public void run() {
                log("run()");
            }
        };
        Thread thread = new Thread(runnable);
        thread.start();

        log("main() end");
    }
}
