package lambda.practice;

public class M1Before {

    public static void main(String[] args) {

        M1Interface m1Interface = hello -> {
            System.out.println("=== 시작 ===");
            System.out.println(hello);
            System.out.println("=== 끝 ===");
        };
        m1Interface.helloMessage("Good Morning!");
        m1Interface.helloMessage("Good Afternoon!");
        m1Interface.helloMessage("Good Evening!");

    }
}
