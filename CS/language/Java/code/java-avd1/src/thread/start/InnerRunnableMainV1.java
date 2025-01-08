package thread.start;

import static util.MyLogger.log;

public class InnerRunnableMainV1 {

    public static void main(String[] args) {

        log("main() start");

        Runnable runnable = new MyRunnable();
        Thread thread = new Thread(runnable);
        thread.start();

        log("main() end");
    }

    // 중첩 클래스 : 여러 군데에서 안쓸거 같고 이 class 안에서만 사용할거 같을 때 사용
    static class MyRunnable implements Runnable{
        @Override
        public void run() {
            log(": run()");
        }
    }
}
