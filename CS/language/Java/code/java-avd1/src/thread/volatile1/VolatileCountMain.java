package thread.volatile1;


import static util.MyLogger.log;
import static util.ThreadUtils.sleep;

public class VolatileCountMain {

    public static void main(String[] args) {
        MyTask myTask = new MyTask();
        Thread t = new Thread(myTask);
        t.start();
        sleep(1000);

        myTask.flag = false;

        log("flag : " + myTask.flag + ", count : " + myTask.count + " in main");

    }

    static class MyTask implements Runnable{
        volatile boolean flag = true;
        volatile long count;
//        long count;
//        boolean flag = true;

        @Override
        public void run() {
            while (flag){
                count++;
                if (count % 100_000_000 == 0){
                    log("flag = " + flag + ", count = " + count + " in while()");
                }
            }
            log("flag = " + flag + ", count = "+ count + " end");
        }
    }

}
