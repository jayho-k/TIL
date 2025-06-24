package lambda.start;

import lambda.Procedure;

import java.util.Random;

public class Ex1RefMain {


    public static void hello(Procedure procedure) {
        long startNs = System.nanoTime();

        procedure.run();

        long endNs = System.nanoTime();
        System.out.println("timestamp " + (endNs - startNs));
    }

    static class Dice implements Procedure {

        @Override
        public void run() {
            int randomValue = new Random().nextInt(6) + 1;
            System.out.println("dice " + randomValue);
        }
    }

    public static void main(String[] args) {
        hello(new Dice());
    }
}
