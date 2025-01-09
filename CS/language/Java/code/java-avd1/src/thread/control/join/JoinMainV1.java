package thread.control.join;

import static util.MyLogger.log;
import static util.ThreadUtils.sleep;

public class JoinMainV1 {

    public static void main(String[] args) {
        log("Start");

        SumTask sumTask1 = new SumTask(1,50);
        SumTask sumTask2 = new SumTask(51, 100);

        Thread thread1 = new Thread(sumTask1);
        Thread thread2 = new Thread(sumTask2);

        thread1.start();
        thread2.start();

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
