import java.util.Arrays;
import java.util.HashMap;
import java.util.Map;

public class Main {
    public static void main(String[] args) throws InterruptedException {


        System.out.println(Integer.toBinaryString(999 << 16));
        System.out.println(Integer.toBinaryString(999 >> 16));
        System.out.println(Integer.toBinaryString(999 >>> 16));
        System.out.println(Integer.toBinaryString(1 << 30));
        System.out.println(Integer.toBinaryString(1 << 30));
        System.out.println((1 << 27));
        System.out.println((1 << 28));
        System.out.println((1 << 29));
        System.out.println((1 << 30));
        System.out.println((1 << 31));

//        for (int binCount = 0; ; ++binCount) {
//            Thread.sleep(1000);
//            System.out.println(binCount);
//        }

    }
}