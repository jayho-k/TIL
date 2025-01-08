package quiz.start.q1;

import static util.MyLogger.log;

public class StartTest4Main {

    public static void main(String[] args) {
        log("main() start");

        Thread threadA = new Thread(new CounterThread("A",1000), "Thread-A");
        threadA.start();

        Thread threadB = new Thread(new CounterThread("B",500));
        threadB.start();

        log("main() end");
    }

    static class CounterThread implements Runnable{

        private final String type;
        private final int time;

        public CounterThread(String type, int time){
            this.type = type;
            this.time = time;
        }

        @Override
        public void run() {
            while(true){
                log(type);
                try {
                    Thread.sleep(time);
                } catch (InterruptedException e) {
                    throw new RuntimeException(e);
                }
            }
        }
    }

}
