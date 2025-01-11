package thread.volatile1;

import static util.MyLogger.log;
import static util.ThreadUtils.sleep;

public class VolatileFlagMain {

    public static void main(String[] args) {

        MyTask myTask = new MyTask();
        Thread t = new Thread(myTask);
        t.start();

        sleep(1000);
        myTask.runFlag = false;
        log("run flag : " + myTask.runFlag);
        log("main end");

    }

    static class MyTask implements Runnable{
        //boolean runFlag = true;

        volatile boolean runFlag = true;

        @Override
        public void run() {
            log("task start");
            while (runFlag){
                // runFlag가 false로 변하지 않음
            }
            log("task end");
        }
    }



}
