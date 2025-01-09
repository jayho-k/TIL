package thread.control.join;

import static util.MyLogger.log;
import static util.ThreadUtils.sleep;

public class JoinMainV2 {

    public static void main(String[] args) throws InterruptedException {
        log("Start");

        SumTask sumTask1 = new SumTask(1,50);
        SumTask sumTask2 = new SumTask(51, 100);

        Thread thread1 = new Thread(sumTask1);
        Thread thread2 = new Thread(sumTask2);

        thread1.start();
        thread2.start();

        // thread 가 종료될 떄 까지 대기 -> 1번 2번이 종료될 때 까지 대기하게 된다.
        // 완료가 되자마자 바로 깨어남
        log("join() start");
        thread1.join();
        thread2.join();
        log("join() end");


        log("1: " + sumTask1.result);
        log("2: " + sumTask2.result);

        int resultAll = sumTask1.result + sumTask2.result;
        log("all : " + resultAll);

        log("End");
    }


    static class SumTask implements Runnable{

        int startValue;
        int endValue;
        int result = -1;

        public SumTask(int startValue, int endValue){
            this.startValue = startValue;
            this.endValue = endValue;
        }

        @Override
        public void run() {
            sleep(2000);
            int sum = 0;
            for (int i = startValue; i<=endValue; i++){
                sum += i;
            }
            result = sum;
            log(result);
            log("Run End");
        }
    }

}
