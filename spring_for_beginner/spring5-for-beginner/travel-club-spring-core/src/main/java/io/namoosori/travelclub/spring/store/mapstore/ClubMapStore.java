package io.namoosori.travelclub.spring.store.mapstore;


import io.namoosori.travelclub.spring.aggregate.club.TravelClub;
import io.namoosori.travelclub.spring.store.ClubStore;
import org.springframework.stereotype.Repository;

import java.util.LinkedHashMap;
import java.util.List;
import java.util.Map;
import java.util.Optional;
import java.util.stream.Collectors;

// interface를 implement하기 위해선 implements를 써주면 된다.
// Art enter를 누르면 자동으로 generate된다. (interface에서 정의한 것들)

@Repository
public class ClubMapStore implements ClubStore {

    // key값은 String, 저장되는 객체는 TravelClub으로 저장한다는 뜻
    // 생성자 정의
    private Map<String, TravelClub> clubMap;
    private ClubMapStore(){
        this.clubMap = new LinkedHashMap<>();
    }

    // 새로 저장되는 TravelClub의 정보가 들어오게 된다.
    //
    @Override
    public String create(TravelClub club) {
        clubMap.put(club.getId(), club);
        return club.getId();
    }

    @Override
    public TravelClub retrieve(String clubId) {
        return clubMap.get(clubId);
    }
    @Override // collect에 대해서 알아보기
    public List<TravelClub> retrieveByName(String name) {
        return clubMap.values().stream()
                .filter(club -> club.getName().equals(name))
                .collect(Collectors.toList());
    }

    @Override // club에 있는 id값을 불러와서 club으로 바꿔주면 되는 것
    public void update(TravelClub club) {
        System.out.println("club.getId : " + club.getId());
        System.out.println("club : " + club);
        clubMap.put(club.getId(), club);
    }

    @Override
    public void delete(String clubId) {
        clubMap.remove(clubId);
    }

    @Override
    public boolean exists(String clubId) {
//        return clubMap.containsKey(clubId);
        return Optional.ofNullable(clubMap.get(clubId)).isPresent();
    }
}
