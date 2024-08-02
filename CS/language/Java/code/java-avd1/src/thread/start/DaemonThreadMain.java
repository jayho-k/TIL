package thread.start;

public class DaemonThreadMain {

    public static void main(String[] args) {
        System.out.println(Thread.currentThread().getName() + ": main start");

        DaemonThread daemonThread = new DaemonThread();
        daemonThread.setDaemon(true); // daemon thread 여부 설정하기
        daemonThread.start();

        System.out.println(Thread.currentThread().getName() + ": main end");


    }

    static class DaemonThread extends Thread{

        @Override
        public void run(){
            System.out.println(Thread.currentThread().getName() + ": run()");


            // throw를 밖으로 던질 수 없다. run에서는 무조건 예외를 안에서 잡아야한다.
            try {
                Thread.sleep(10000); // 10초간 실행
            } catch (InterruptedException e) {
                throw new RuntimeException(e);
            }

            System.out.println(Thread.currentThread().getName() + ": run() end");
        }
    }

}
