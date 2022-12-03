package io.namoosori.travelclub.spring;

import io.namoosori.travelclub.spring.aggregate.club.CommunityMember;
import io.namoosori.travelclub.spring.aggregate.club.TravelClub;
import io.namoosori.travelclub.spring.service.ClubService;
import io.namoosori.travelclub.spring.service.MemberService;
import io.namoosori.travelclub.spring.service.sdo.MemberCdo;
import io.namoosori.travelclub.spring.service.sdo.TravelClubCdo;
import io.namoosori.travelclub.spring.store.ClubStore;
import org.springframework.context.ApplicationContext;
import org.springframework.context.support.ClassPathXmlApplicationContext;

import java.util.Arrays;
import java.util.Date;

public class TravelClubApp {

    public static void main(String[] args){
        ApplicationContext context = new ClassPathXmlApplicationContext("applicationContext.xml");

        String [] beanNames = context.getBeanDefinitionNames();
//        System.out.println(Arrays.toString(beanNames));

        MemberService memberService = context.getBean("memberServiceLogic", MemberService.class);
        String memberId = memberService.registerMember(
                new MemberCdo(
                        "test@test.com",
                        "kang",
                        "testMemebr",
                        "010-1111-1111",
                        "2020.12.12"));

        CommunityMember foundedMember = memberService.findMemberById(memberId);
        System.out.println(foundedMember.toString());


//        TravelClubCdo clubCdo = new TravelClubCdo("TravelClub", "Test TravelClub");
//        ClubService clubService = context.getBean("clubService", ClubService.class);
//
//        String clubId = clubService.registerClub(clubCdo);
//        TravelClub foundedClub = clubService.findClubById(clubId);
//        System.out.println("ID : " + foundedClub.getName());
//        System.out.println("intro : " + foundedClub.getIntro());
//        System.out.println("foundation : " + new Date(foundedClub.getFoundationTime()));



    }

}
