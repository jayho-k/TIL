package io.namoosori.travelclub.spring.store.mapstore;

import io.namoosori.travelclub.spring.aggregate.club.CommunityMember;
import io.namoosori.travelclub.spring.store.MemberStore;
import org.springframework.stereotype.Repository;

import javax.swing.text.html.Option;
import java.util.LinkedHashMap;
import java.util.List;
import java.util.Map;
import java.util.Optional;
import java.util.stream.Collectors;

@Repository
public class MemberMapStore implements MemberStore {

    private Map<String, CommunityMember> memberMap;

    public MemberMapStore(){
        this.memberMap = new LinkedHashMap<>();
    }

    @Override
    public String create(CommunityMember member) {
        memberMap.put(member.getId(), member);
        return member.getId();
    }

    @Override
    public CommunityMember retrieve(String memberId) {
        return memberMap.get(memberId);
    }

    @Override
    public CommunityMember retrieveByEmail(String email) {
        CommunityMember targetMember = null;
        for (CommunityMember member : memberMap.values()){
            if (member.getEmail().equals(email)){
                targetMember = member;
                break;
            }
        }
        return targetMember;
    }

    @Override
    public List<CommunityMember> retrieveByName(String name) {
        return memberMap.values().stream()
                .filter(member -> member.getName().equals(name))
                .collect(Collectors.toList());
    }

    @Override
    public void update(CommunityMember member) {
        // member는 이미 업데이트된 것들이 넘어 올 것이다. 따라서 그냥 put으로 넣어주면 됨
        memberMap.put(member.getId(), member);
    }

    @Override
    public void delete(String memberId) {
        memberMap.remove(memberId);
    }

    @Override
    public boolean exists(String memberId) {
        return Optional.ofNullable(memberMap.get(memberId)).isPresent();
    }
}
