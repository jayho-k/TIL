package thread.start;

public class HelloTread extends Thread{

    @Override
    public void run(){
        System.out.println(Thread.currentThread().getName() + ": run()");
    }

}
