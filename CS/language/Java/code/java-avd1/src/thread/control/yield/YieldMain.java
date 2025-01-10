package thread.control.yield;

import static util.ThreadUtils.sleep;

public class YieldMain {

    static final int THREAD_COUNT = 1000;

    public static void main(String[] args) {
        for (int i = 0; i < THREAD_COUNT; i++){
            Thread thread = new Thread(new MyRunnable());
            thread.start();
        }
    }


    static class MyRunnable implements Runnable{

        @Override
        public void run() {
            for(int i = 0; i<10; i++){
                System.out.println(Thread.currentThread().getName() + " - " + i);
                //  x : 1번 방법 => 한 스레드가 계속 많이 실행되는 모습을 보임
                //sleep(1); // 2번 방법 => 계속 thread 가 바뀌는 모습을 보고 있다.
                Thread.yield(); // 3번 방법 => thread의 상태는 동일(runnable) 하지만 대기열애 들어가는 상황
            }
        }
    }



}
