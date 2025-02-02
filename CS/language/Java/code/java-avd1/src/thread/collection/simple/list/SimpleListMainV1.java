package thread.collection.simple.list;

import static util.MyLogger.log;

public class SimpleListMainV1 {

    public static void main(String[] args) throws InterruptedException {
        //SimpleList list = new BasicList();
        //SimpleList list = new SyncList();
        SimpleList list = new SyncProxyList(new BasicList());
        test(list);
    }

    private static void test(SimpleList list) throws InterruptedException {

        log(list.getClass().getSimpleName());

        Runnable runnableA = new Runnable() {
            @Override
            public void run() {
                list.add("A");
                log("Thread 1 : list add A");
            }
        };

        Runnable runnableB = new Runnable() {
            @Override
            public void run() {
                list.add("B");
                log("Thread 2 : list add B");
            }
        };

        Thread t1 = new Thread(runnableA, "Thread 1");
        Thread t2 = new Thread(runnableB, "Thread 2");

        t1.start();
        t2.start();

        t1.join();
        t2.join();

        log(list);
    }


}
