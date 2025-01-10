package thread.control.interrupt;

import static util.MyLogger.log;
import static util.ThreadUtils.sleep;

public class ThreadStopMainV4 {

    public static void main(String[] args) {

        MyTask myTask = new MyTask();
        Thread thread = new Thread(myTask);
        thread.start();

        sleep(20);

        log("중단 지시 : thread.control.interrupt();");
        thread.interrupt();
        log("interrupt 상태 1 : " + thread.isInterrupted());
    }


    static class MyTask implements Runnable{

        @Override
        public void run() {
            while(!Thread.interrupted()){
                log("시작");
            }

            log("interrupt 상태 2 : " + Thread.currentThread().isInterrupted());
            log("thread 상태 : " + Thread.currentThread().getState());

            try {
                log("자원 정리 시작");
                Thread.sleep(1000);
                log("interrupt 상태 3 : " + Thread.currentThread().isInterrupted());
                log("자원 정리 종료");
            } catch (InterruptedException e) {
                log("interrupt 상태 4 : " + Thread.currentThread().isInterrupted());
            }

        }
    }


}
