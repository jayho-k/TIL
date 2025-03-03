package kube.board.view.service;

import kube.board.view.repository.ArticleViewCountRepository;
import kube.board.view.repository.ArticleViewDistributedLockRepository;
import lombok.RequiredArgsConstructor;
import org.springframework.stereotype.Service;

import java.time.Duration;

@Service
@RequiredArgsConstructor
public class ArticleViewService {

    private final ArticleViewCountRepository articleViewCountRepository;
    private final ArticleViewCountBackUpProcessor articleViewCountBackUpProcessor;
    private final ArticleViewDistributedLockRepository articleViewDistributedLockRepository;

    private static final int BACK_UP_BATCH_SIZE = 100;
    private static final Duration TTL = Duration.ofMinutes(10);


    public Long increase(Long articleId, Long userId){

        // 분산락을 통한 Abusing 정책 적용 : (article, user)의 조회수 10분당 1회 가능하도록
        if (!articleViewDistributedLockRepository.lock(articleId, userId, TTL)){
            return articleViewCountRepository.read(articleId);
        }

        // increase
        Long count = articleViewCountRepository.increase(articleId);

        // count 100번 당 back up 시도 [-> MySQL]
        if (count % BACK_UP_BATCH_SIZE == 0){
            articleViewCountBackUpProcessor.backUp(articleId, count);
        }
        return count;
    }

    public Long count(Long articleId){
        return articleViewCountRepository.read(articleId);
    }

}
