package lambda.practice;


import lambda.Procedure;

import java.util.Arrays;

public class M3Before {

    public static void measure(Procedure p) {
        long startTime = System.currentTimeMillis();
        p.run();
        long endTime = System.currentTimeMillis();
        System.out.println(endTime-startTime);
    }

    public static void main(String[] args) {

        Procedure p1 = () -> {
            int N = 100;
            long sum = 0;
            for (int i = 1; i <= N; i++) {
                sum += i;
            }
        };
        Procedure p2 = () -> {
            int[] arr = { 4, 3, 2, 1 };
            System.out.println("원본 배열: " + Arrays.toString(arr));
            Arrays.sort(arr);
            System.out.println("배열 정렬: " + Arrays.toString(arr));
        };

        measure(p1);
        measure(p2);




    }
}
