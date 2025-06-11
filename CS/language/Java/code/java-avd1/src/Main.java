import java.util.HashMap;
import java.util.Map;

public class Main {
    public static void main(String[] args) throws InterruptedException {
        for (int binCount = 0; ; ++binCount) {
            Thread.sleep(1000);
            System.out.println(binCount);
        }

    }
}