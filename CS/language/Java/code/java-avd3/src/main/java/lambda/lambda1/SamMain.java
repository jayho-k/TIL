package lambda.lambda1;

public class SamMain {

    public static void main(String[] args) {

        // interface에 함수가 1개라서 가능
        SamInterface samInterface = () -> {
            System.out.println("sam");
        };
        samInterface.run();

        // interface에 함수가 2개라서 안됨
//        NotSamInterface notSamInterface = () -> {
//            System.out.println("asdf");
//        };
//        notSamInterface.go();
    }

}
