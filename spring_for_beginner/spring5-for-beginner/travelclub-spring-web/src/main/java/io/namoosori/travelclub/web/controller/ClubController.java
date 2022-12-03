package io.namoosori.travelclub.web.controller;

import io.namoosori.travelclub.web.aggregate.club.TravelClub;
import io.namoosori.travelclub.web.service.ClubService;
import io.namoosori.travelclub.web.service.sdo.TravelClubCdo;
import io.namoosori.travelclub.web.shared.NameValueList;
import org.springframework.web.bind.annotation.*;

import java.util.List;

@RestController
@RequestMapping("/club")
public class ClubController {

    private ClubService clubService;

    public ClubController(ClubService clubService) {
        this.clubService = clubService;
    }

    @PostMapping
    public String register(@RequestBody TravelClubCdo travelClubCdo) {
        return clubService.registerClub(travelClubCdo);
    }

    @GetMapping("/all")
    public List<TravelClub> findAll() {
        return clubService.findAll();
    }

    @GetMapping("/{clubId}")
    public TravelClub find(@PathVariable String clubId) {
        return clubService.findClubById(clubId);
    }

    @GetMapping
    public List<TravelClub> findByName(@RequestParam String name) {
        return clubService.findClubsByName(name);
    }

    @PutMapping("/{clubId}")
    public void modify(@PathVariable String clubId,@RequestBody NameValueList nameValueList) {
        clubService.modify(clubId, nameValueList);
    }

    @DeleteMapping("/{clubId}")
    public void delete(@PathVariable String clubId) {
        clubService.remove(clubId);
    }
}
