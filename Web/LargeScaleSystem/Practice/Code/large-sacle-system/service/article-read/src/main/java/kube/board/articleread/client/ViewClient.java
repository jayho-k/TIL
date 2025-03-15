package kube.board.articleread.client;

import jakarta.annotation.PostConstruct;
import lombok.RequiredArgsConstructor;
import lombok.extern.slf4j.Slf4j;
import org.springframework.beans.factory.annotation.Value;
import org.springframework.cache.annotation.Cacheable;
import org.springframework.stereotype.Component;
import org.springframework.web.client.RestClient;

@Slf4j
@Component
@RequiredArgsConstructor
public class ViewClient {

    private RestClient restClient;

    @Value("${endpoints.large-scale-system-view-service.url}")
    private String viewServiceUrl;

    @PostConstruct
    public void initRestClient(){
        restClient = RestClient.create(viewServiceUrl);
    }

    // redis에서 데이터 조회
    // redis data가 없다면, count 메소드 내부 로직 호출, viewService로 원본 데이터 요청
    // redis 에 data를 넣고 응답
    // redis 에 데이터가 있었다면, 그 데이터를 반환한다.
    @Cacheable(key = "#articleId", value = "articleViewCount")
    public long count(Long articleId){
        log.info("[ViewClient.count] articleId={}", articleId);
        try{
            return restClient.get()
                    .uri("/v1/article-views/articles/{articleId}/count", articleId)
                    .retrieve()
                    .body(Long.class);
        }catch (Exception e){
            log.error("[ViewClient.count] articleId={}", articleId, e);
            return 0;
        }
    }





}
