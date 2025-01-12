package quiz.sync;

import java.util.ArrayList;
import java.util.List;

import static util.MyLogger.log;

public class SyncTest2Main {


    public static void main(String[] args) throws InterruptedException {

        TreadTest treadTest1 = new TreadTest(10, new Test());
        TreadTest treadTest2 = new TreadTest(10, new Test());

        Thread t1 = new Thread(treadTest1, "t1");
        Thread t2 = new Thread(treadTest2, "t2");

        t1.start();
        t2.start();

        t1.join();
        t2.join();

        List<String> sysOutList1 = treadTest1.sysOutList;
        log(sysOutList1.stream().count());

        sysOutList1.stream().forEach(
                s-> log(s)
        );

        List<String> sysOutList2 = treadTest2.sysOutList;
        log(sysOutList2.stream().count());

        sysOutList2.stream().forEach(
                s-> log(s)
        );

    }

    static class TreadTest implements Runnable {
        List<String> lst;

        public List<String> sysOutList = new ArrayList<>();

        private final Test test;

        public TreadTest(int maxVal, Test test){
            List<String> lst = new ArrayList<>();
            for (int i = 0; i< maxVal; i++){
                lst.add(String.valueOf(i));
            }
            this.lst = lst;
            this.test = test;
        }

        @Override
        public void run() {
            lst.stream().forEach(
                s -> {
                    test.setThreadLocal(s);
                    sysOutList.add("thread name : " + Thread.currentThread().getName() + ", thread key,val : " + test.getThreadLocal() +", " +test.getThreadLocal());
            });

//            synchronized (this){
//                lst.stream().forEach(
//                    s -> {
//                        test.setThreadLocal(s);
//                        sysOutList.add("thread name : " + Thread.currentThread().getName() + ", thread val : " + test.getThreadLocal());
//                });
//            }

        }
    }

    static class Test{
        ThreadLocal<String> threadLocal = new ThreadLocal<>();

        public void setThreadLocal(String s){
            threadLocal.set(s);
        }

        public String getThreadLocal(){
            return threadLocal.get();
        }
    }

}
