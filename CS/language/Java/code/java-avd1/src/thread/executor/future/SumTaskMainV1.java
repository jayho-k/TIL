package thread.executor.future;

import java.util.concurrent.*;

import static util.MyLogger.log;

public class SumTaskMainV1 {


    public static void main(String[] args) throws ExecutionException, InterruptedException {

        SumTask task1 = new SumTask(1, 50);
        SumTask task2 = new SumTask(51, 100);
        ExecutorService es = Executors.newFixedThreadPool(2);

        Future<Integer> future1 = es.submit(task1);
        Future<Integer> future2 = es.submit(task2);

        Integer sum1 = future1.get();
        Integer sum2 = future2.get();

        log("task1 res = " + sum1);
        log("task2 res = " + sum2);

        int sumAll = sum1 + sum2;
        log("sumAll = " + sumAll);

        es.shutdown();
    }

    static class SumTask implements Callable<Integer>{

        int startValue;
        int endValue;

        public SumTask(int startValue, int endValue){
            this.startValue = startValue;
            this.endValue = endValue;
        }

        @Override
        public Integer call() throws Exception {

            log("start");
            int sum = 0;
            for (int i = startValue; i <= endValue; i++){
                sum += i;
            }
            log("end, res = " + sum);

            return sum;
        }
    }




}
