package lambda.practice;

public class M2Before {

    public static void print1() {
        System.out.println("무게: 10kg");
    }
    public static void print2() {
        System.out.println("무게: 50kg");
    }
    public static void print3() {
        System.out.println("무게: 200g");
    }
    public static void print4() {
        System.out.println("무게: 40g");
    }
    public static void main(String[] args) {

        M2Interface m2 = (kg) -> System.out.printf("무게: %dg%n", kg);
        m2.getKg(10);
        m2.getKg(50);
        m2.getKg(200);
        m2.getKg(40);
    }
}
