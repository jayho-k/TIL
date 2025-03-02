package kube.board.view.service;

import kube.board.view.entity.ArticleViewCount;
import kube.board.view.repository.ArticleViewCountBackUpRepository;
import lombok.RequiredArgsConstructor;
import org.springframework.stereotype.Component;
import org.springframework.transaction.annotation.Transactional;

@Component
@RequiredArgsConstructor
public class ArticleViewCountBackUpProcessor {

    private final ArticleViewCountBackUpRepository articleViewCountBackUpRepository;

    @Transactional
    public void backUp(Long articleId, Long viewCount){
        int result = articleViewCountBackUpRepository.updateViewCount(articleId, viewCount);
        if (result == 0){
            articleViewCountBackUpRepository.findById(articleId)
                    // data가 있으면 무시, 없으면 init
                    .ifPresentOrElse(ignored -> {},
                        () -> articleViewCountBackUpRepository.save(
                                ArticleViewCount.init(articleId, viewCount)
                        )
                    );
        }

    }


}
