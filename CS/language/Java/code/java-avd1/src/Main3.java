import java.time.Instant;

public class Main3 {

    public static void main(String[] args) {
        long epochMillis = Instant.now().toEpochMilli(); // or .getEpochSecond()
        System.out.println(epochMillis);

        // 1752585885306
        // 1752585973558
        // 1752585999961
//        System.out.println(1752585999961L-1752585973558L);
        System.out.println(26403/1000);

    }

}
