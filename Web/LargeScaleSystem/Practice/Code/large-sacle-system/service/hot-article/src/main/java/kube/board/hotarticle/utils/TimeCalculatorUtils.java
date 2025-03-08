package kube.board.hotarticle.utils;

import java.time.Duration;
import java.time.LocalDateTime;
import java.time.LocalTime;

public class TimeCalculatorUtils {

    public static Duration calculateDurationToMidnight(){
        // 현재시간에서 자정까지 얼마나 남았는지
        LocalDateTime now = LocalDateTime.now();
        LocalDateTime midnight = now.plusDays(1).with(LocalTime.MIDNIGHT); // The time of midnight at the start of the day, '00:00'.
        return Duration.between(now, midnight);
    }



}
