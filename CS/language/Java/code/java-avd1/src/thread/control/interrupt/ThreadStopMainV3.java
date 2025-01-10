package thread.control.interrupt;

import static util.MyLogger.log;
import static util.ThreadUtils.sleep;

public class ThreadStopMainV3 {

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
            while(!Thread.currentThread().isInterrupted()){
                log("시작");
            }
            log("interrupt 상태 2 : " + Thread.currentThread().isInterrupted());
            log("thread 상태 : " + Thread.currentThread().getState());
        }
    }


}
