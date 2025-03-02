package kube.board.article.service;

import kube.board.article.entity.Article;
import kube.board.article.entity.BoardArticleCount;
import kube.board.article.repository.ArticleRepository;
import kube.board.article.repository.BoardArticleCountRepository;
import kube.board.article.service.request.ArticleCreateRequest;
import kube.board.article.service.request.ArticleUpdateRequest;
import kube.board.article.service.response.ArticlePageResponse;
import kube.board.article.service.response.ArticleResponse;
import kube.board.common.snowflake.Snowflake;
import lombok.RequiredArgsConstructor;
import org.springframework.stereotype.Service;
import org.springframework.transaction.annotation.Transactional;

import java.util.List;

@Service
@RequiredArgsConstructor
public class ArticleService {

    private final Snowflake snowflake = new Snowflake();
    private final ArticleRepository articleRepository;
    private final BoardArticleCountRepository boardArticleCountRepository;


    @Transactional
    public ArticleResponse create(ArticleCreateRequest request){
        Article article = articleRepository.save(
                Article.create(snowflake.nextId(), request.getTitle(), request.getContent(), request.getBoardId(), request.getWriterId())
        );
        int result = boardArticleCountRepository.increase(request.getBoardId());
        if (result == 0){
            boardArticleCountRepository.save(
                    BoardArticleCount.init(request.getBoardId(), 1L)
            );
        }

        return ArticleResponse.from(article);
    }

    @Transactional
    public ArticleResponse update(Long articleId, ArticleUpdateRequest request){
        Article article = articleRepository.findById(articleId).orElseThrow();
        article.update(request.getTitle(), request.getContent());
        return ArticleResponse.from(article);
    }

    public ArticleResponse read(Long articleId){
        return ArticleResponse.from(articleRepository.findById(articleId).orElseThrow());
    }

    public void delete(Long articleId){
        Article article = articleRepository.findById(articleId).orElseThrow();
        articleRepository.delete(article);
        boardArticleCountRepository.decrease(article.getArticleId());
    }

    public ArticlePageResponse readAll(Long boardId, Long page, Long pageSize) {
        // [articles, article count]
        return ArticlePageResponse.of(
                // mapping => ArticleResponse 로 변경
                articleRepository.findAll(boardId, (page - 1) * pageSize, pageSize).stream()
                        .map(ArticleResponse::from)
                        .toList(),
                articleRepository.count(
                        boardId,
                        PageLimitCalculator.calculatePageLimit(page, pageSize, 10L))
        );
    }


    public List<ArticleResponse> readAllInfiniteScroll(Long board_id, Long pageSize, Long lastArticle){
        List<Article> articles = lastArticle == null ?
                articleRepository.findAllInfiniteScroll(board_id, pageSize) :
                articleRepository.findAllInfiniteScroll(board_id, pageSize, lastArticle);
        return articles.stream().map(ArticleResponse::from).toList();
    }

    public Long count(Long boardId) {
        return boardArticleCountRepository.findById(boardId)
                .map(BoardArticleCount::getArticleCount)
                .orElse(0L);
    }

}
