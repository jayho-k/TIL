package lambda.lambda1;


@FunctionalInterface // 함수가 하나라는 것을 명시해주는 것, 2개면 compile error
public interface SamInterface {

    // interface는 기본적으로 앞에 abstract가 붙어 있음
    void run();

}
