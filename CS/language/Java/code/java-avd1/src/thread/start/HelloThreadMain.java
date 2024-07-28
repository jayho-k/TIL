package thread.start;

public class HelloThreadMain {

    public static void main(String[] args){
        System.out.println(Thread.currentThread().getName() + ": main() start");

        HelloTread helloTread = new HelloTread();

        // helloTread.run(); run을 호출하면 안된다.
        // main이 run을 돌리게 되면 main에서 run 메서드를 실행하게 된다.
        System.out.println(Thread.currentThread().getName() + ": start 호출 전");
        helloTread.start();
        System.out.println(Thread.currentThread().getName() + ": start 호출 후");

        System.out.println(Thread.currentThread().getName() + ": main() end");
    }


}
