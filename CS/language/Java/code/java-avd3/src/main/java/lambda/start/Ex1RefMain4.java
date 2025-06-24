package lambda.start;

import lambda.Procedure;

import java.util.Random;

public class Ex1RefMain4 {


    public static void hello(Procedure procedure) {
        long startNs = System.nanoTime();

        procedure.run();

        long endNs = System.nanoTime();
        System.out.println("timestamp " + (endNs - startNs));
    }

    public static void main(String[] args) {

        hello(() -> {
            int randomValue = new Random().nextInt(6) + 1;
            System.out.println("dice " + randomValue);
        });

    }
}
