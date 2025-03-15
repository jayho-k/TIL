package kube.board.articleread.learning;

import org.junit.jupiter.api.Test;

public class LongToDoubleTest {

    @Test
    void longToDoubleTest(){
        // long : 64bit로 정수
        // double : 64bit로 부동소수점 => double이 long을 정밀하게 표현하기 못하는 상황발생

        long longValue = 111_111_111_111_111_111L; //111111111111111111
        System.out.println("longValue = " + longValue);

        double doubleValue = longValue; //111111111111111E17

        System.out.println("doubleValue = " + doubleValue);
        long longValue2 = (long)doubleValue; // 111111111111111104
        System.out.println(longValue2);

    }

}
