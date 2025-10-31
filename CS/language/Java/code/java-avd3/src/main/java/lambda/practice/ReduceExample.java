package lambda.practice;

import java.util.List;

public class ReduceExample {

    // 함수를 인자로 받아, 리스트 요소를 하나로 축약(reduce)하는 고차 함수
    public static int reduce(List<Integer> list, int initial, MyReducer reducer) {
        int res = initial;
        for (int i : list) {
            res = reducer.reduce(initial, i);
            initial = res;
        }
        return res; // 적절한 값으로 변경
    }

    public static void main(String[] args) {
        List<Integer> numbers = List.of(1, 2, 3, 4);
        System.out.println("리스트: " + numbers);
        // 1. 합 구하기 (초깃값 0, 덧셈 로직)
        int res1 = reduce(numbers, 0, (a, b) -> a + b);
        System.out.println(res1);

        // 2. 곱 구하기 (초깃값 1, 곱셈 로직)
        int res2 = reduce(numbers, 1, (a, b) -> a * b);
        System.out.println(res2);
    }

}
