package kube.board.common.outboxmessagerelay;

import lombok.Getter;

import java.util.List;
import java.util.stream.LongStream;

@Getter
public class AssignedShard {
    private List<Long> shards;

    public static AssignedShard of(String appId, List<String> appIds, long shardCount){
        AssignedShard assignedShard = new AssignedShard();
        assignedShard.shards = assign(appId, appIds, shardCount);
        //System.out.println(assignedShard.shards);
        return assignedShard;
    }

    private static List<Long> assign(String appId, List<String> appIds, long shardCount) {
        int appIndex = findAppIndex(appId, appIds); // appId가 몇 번째 있는지 반환하는 함수

        // 할당할 shard가 없는 경우
        if (appIndex == -1){
            return List.of();
        }

        long start = appIndex * shardCount / appIds.size();
        long end = (appIndex + 1) * shardCount / appIds.size() - 1;

        // start ~ end 까지 List
        return LongStream.rangeClosed(start, end).boxed().toList();
    }

    private static int findAppIndex(String appId, List<String> appIds) {
        for (int i=0; i < appIds.size(); i++){
            if (appIds.get(i).equals(appId)){
                return i;
            }
        }
        return -1;
    }
}
