package thread.control.interrupt;

import static util.MyLogger.log;
import static util.ThreadUtils.sleep;

public class ThreadStopMainV1 {

    public static void main(String[] args) {

        MyTask myTask = new MyTask();
        Thread thread = new Thread(myTask);
        thread.start();

        sleep(4000);

        log("중단 지시 : thread.control.interrupt();");
        thread.interrupt();
        log("interrupt 상태 1 : " + thread.isInterrupted());
    }


    static class MyTask implements Runnable{

        @Override
        public void run() {

            try {
                while(true){
                    log("시작");
                    Thread.sleep(3000);
                    log("끝");
                }
            }
            catch (InterruptedException e) {
                log("interrupt 상태 2 : " + Thread.currentThread().isInterrupted());
                log(e.getMessage());
                log("thread 상태 : " + Thread.currentThread().getState());
            }

        }
    }


}
