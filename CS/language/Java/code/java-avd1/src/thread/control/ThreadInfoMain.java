package thread.control;

import thread.start.HelloRunnable;

import static util.MyLogger.log;

public class ThreadInfoMain {


    public static void main(String[] args) {
        // main thread 가져오기
        Thread mainThread = Thread.currentThread();

        log("mainThread = " + mainThread);
        log("mainThread.threadId() = " + mainThread.getId()); // 중복되지 않음
        log("mainThread.getName() = " + mainThread.getName()); // 중복 될 수 있음
        log("mainThread.getPriority() = " + mainThread.getPriority()); // default = 5
        log("mainThread.getState() = " + mainThread.getState()); // runnable thread가 실행 될 수 있는 상태


        Thread myThread = new Thread(new HelloRunnable(), "myThread");
        log("myThread = " + myThread);
        log("myThread.threadId() = " + myThread.getId()); // 중복되지 않음
        log("myThread.getName() = " + myThread.getName()); // 중복 될 수 있음
        log("myThread.getPriority() = " + myThread.getPriority()); // default = 5
        log("myThread.getState() = " + myThread.getState()); // NEW :




    }

}
