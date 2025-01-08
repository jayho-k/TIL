package thread.start;

import static util.MyLogger.log;

public class InnerRunnableMainV3 {
    public static void main(String[] args) {

        log("main() start");

        // lambda 로 가능
        Thread thread = new Thread(() -> log("run()"));
        thread.start();

        log("main() end");
    }
}
