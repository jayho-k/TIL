package kube.board.common.snowflake;

import java.util.random.RandomGenerator;

public class Snowflake {

    private static final int UNUSED_BITS = 1;

    private static final int EPOCH_BITS = 41;

    private static final int NODE_ID_BITS = 10;

    private static final int SEQUENCE_BITS = 12;

    private static final long maxNodeId = (1L<<NODE_ID_BITS) -1;

    private static final long maxSequence = (1L<<SEQUENCE_BITS) - 1;

    private final long nodeId = RandomGenerator.getDefault().nextLong(maxNodeId + 1);

    private final long startTimeMillis = 1704067200000L;

    private long lastTimeMillis = startTimeMillis;

    private long sequence = 0L;

    // id 예시

    //150598734386745971
    //150598734390939804
    //150598734416107110
    //150598734416105494

    public synchronized long nextId(){

        long currentTimeMillis = System.currentTimeMillis();

        // 현재 시간 < 마지막 시간 => Invalid
        if (currentTimeMillis < lastTimeMillis){
            throw new IllegalStateException("Invalid Time");
        }

        // 시간이 같을 경우 => 서로 겹치지 않게 1씩 증가시킴 (속도 때문에 이렇게 진행한듯)
        if (currentTimeMillis == lastTimeMillis){

            // bit 연산 (and) : 둘다 1이여야 1
            sequence = (sequence + 1) & maxSequence;
            if (sequence == 0){
                currentTimeMillis = waitNextMills(currentTimeMillis);
            }

        }else{
            sequence = 0;
        }

        lastTimeMillis = currentTimeMillis;

        return ((currentTimeMillis - startTimeMillis) << (NODE_ID_BITS + SEQUENCE_BITS)) | (nodeId << SEQUENCE_BITS) | sequence;
    }


    private long waitNextMills(long currentTimestamp){
        while (currentTimestamp <= lastTimeMillis){
            currentTimestamp = System.currentTimeMillis();
        }
        return currentTimestamp;
    }







}
