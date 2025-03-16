package kube.board.articleread.controller;

import kube.board.articleread.service.response.ArticleReadPageResponse;
import kube.board.articleread.service.response.ArticleReadResponse;
import kube.board.articleread.service.ArticleReadService;
import lombok.RequiredArgsConstructor;
import org.springframework.web.bind.annotation.GetMapping;
import org.springframework.web.bind.annotation.PathVariable;
import org.springframework.web.bind.annotation.RequestParam;
import org.springframework.web.bind.annotation.RestController;

import java.util.List;

@RestController
@RequiredArgsConstructor
public class ArticleReadController {

    private final ArticleReadService articleReadService;

    @GetMapping("/v1/articles/{articleId}")
    public ArticleReadResponse read(@PathVariable("articleId") Long articleId){
        return articleReadService.read(articleId);
    }

    @GetMapping("/v1/articles")
    public ArticleReadPageResponse readAll(
            @RequestParam("boardId") Long boardId,
            @RequestParam("page") Long page,
            @RequestParam("pageSize") Long pageSize
    ){
        return articleReadService.readAll(boardId, page, pageSize);
    }

    @GetMapping("/v1/articles/infinite-scroll")
    public List<ArticleReadResponse> readAllInfiniteScroll(
            @RequestParam("boardId") Long boardId,
            @RequestParam(value = "lastArticleId", required = false) Long lastArticleId,
            @RequestParam("pageSize") Long pageSize
    ){
        return articleReadService.readAllInfiniteScroll(boardId, lastArticleId, pageSize);
    }

}
