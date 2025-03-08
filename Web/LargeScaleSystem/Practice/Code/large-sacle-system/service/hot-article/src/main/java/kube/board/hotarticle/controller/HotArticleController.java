package kube.board.hotarticle.controller;

import kube.board.hotarticle.service.HotArticleService;
import kube.board.hotarticle.service.response.HotArticleResponse;
import lombok.RequiredArgsConstructor;
import org.springframework.web.bind.annotation.GetMapping;
import org.springframework.web.bind.annotation.PathVariable;
import org.springframework.web.bind.annotation.RestController;

import java.util.List;

@RestController
@RequiredArgsConstructor
public class HotArticleController {

    private final HotArticleService hotArticleService;

    @GetMapping("/v1/hot-articles/article/date/{dateStr}")
    public List<HotArticleResponse> readAll(
            @PathVariable("dateStr") String dateStr
    ){
        return hotArticleService.readAll(dateStr);
    }


}
