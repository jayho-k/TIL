package kube.board.comment.api;

import kube.board.comment.service.request.CommentCreateRequest;

import kube.board.comment.service.response.CommentPageResponse;
import kube.board.comment.service.response.CommentResponse;
import lombok.AllArgsConstructor;
import lombok.Getter;
import org.junit.jupiter.api.Test;
import org.springframework.core.ParameterizedTypeReference;
import org.springframework.web.client.RestClient;

import java.util.List;

public class CommentApiTest {

    RestClient restClient = RestClient.create("http://localhost:9001");

    @Test
    void create(){
        CommentResponse response1 = createComment(new CommentCreateRequest(1L, "my comment1", null, 1L));
        CommentResponse response2 = createComment(new CommentCreateRequest(1L, "my comment2", response1.getParentCommentId(), 1L));
        CommentResponse response3 = createComment(new CommentCreateRequest(1L, "my comment3", response1.getParentCommentId(), 1L));

        System.out.println("commentId 1 = " + response1.getCommentId());
        System.out.println("commentId 2 = " + response2.getCommentId());
        System.out.println("commentId 3 = " + response3.getCommentId());

//        commenntId 1 = 153792214256201728
//        commenntId 2 = 153792215942311936
//        commenntId 3 = 153792216101695488
    }


    CommentResponse createComment(CommentCreateRequest request) {
        return restClient.post()
                .uri("/v1/comments")
                .body(request)
                .retrieve()
                .body(CommentResponse.class);
    }

    @Test
    void read(){
        CommentResponse response = restClient.get()
                .uri("/v1/comments/{commentId}")
                .retrieve()
                .body(CommentResponse.class);
        System.out.println("res = " + response);
    }

    @Test
    void delete(){
        restClient.delete()
                .uri("/v1/comments/{commentId}", 153792214256201728L)
                .retrieve();

//        commenntId 1 = 153792214256201728
//        commenntId 2 = 153792215942311936
//        commenntId 3 = 153792216101695488
    }


    // 1번 page 조회 결과
//response.getCommentCount() = 101
//comment.getCommentId() = 153792214256201728
//	comment.getCommentId() = 153792215942311936
//	comment.getCommentId() = 153792216101695488
//comment.getCommentId() = 153796807288729600
//	comment.getCommentId() = 153796807385198600
//comment.getCommentId() = 153796807288729601
//	comment.getCommentId() = 153796807385198598
//comment.getCommentId() = 153796807288729602
//	comment.getCommentId() = 153796807385198595
//comment.getCommentId() = 153796807288729603
    @Test
    void readAll(){
        CommentPageResponse response = restClient.get()
                .uri("/v1/comments?articleId=1&page=1&pageSize=10")
                .retrieve()
                .body(CommentPageResponse.class);

        System.out.println("response.getCommentCount() = " + response.getCommentCount());
        for (CommentResponse comment : response.getComments()) {
            // comment id 가 자기 자신이 아니면 depth를 가지고 있다는 뜻
            if (!comment.getCommentId().equals(comment.getParentCommentId())){
                System.out.print("\t");
            }
            System.out.println("comment.getCommentId() = " + comment.getCommentId());
        }
    }

    @Test
    void readAllInfiniteScroll() {
        List<CommentResponse> response1 = restClient.get()
                .uri("/v1/comments/infinite-scroll?articleId=1&pageSize=5")
                .retrieve()
                .body(new ParameterizedTypeReference<List<CommentResponse>>() {
                });
        System.out.println("firstPage");

        for (CommentResponse comment : response1) {
            // comment id 가 자기 자신이 아니면 depth를 가지고 있다는 뜻
            if (!comment.getCommentId().equals(comment.getParentCommentId())){
                System.out.print("\t");
            }
            System.out.println("comment.getCommentId() = " + comment.getCommentId());
        }

        Long lastParentCommentId = response1.getLast().getParentCommentId();
        Long lastCommentId = response1.getLast().getCommentId();

        System.out.println("secondPage");

        List<CommentResponse> response2 = restClient.get()
                .uri("/v1/comments/infinite-scroll?articleId=1&pageSize=5&lastParentCommentId=%s&lastCommentId=%s"
                        .formatted(lastParentCommentId,lastCommentId))
                .retrieve()
                .body(new ParameterizedTypeReference<List<CommentResponse>>() {
                });

        for (CommentResponse comment : response2) {
            // comment id 가 자기 자신이 아니면 depth를 가지고 있다는 뜻
            if (!comment.getCommentId().equals(comment.getParentCommentId())){
                System.out.print("\t");
            }
            System.out.println("comment.getCommentId() = " + comment.getCommentId());
        }
    }

    @Getter
    @AllArgsConstructor
    public static class CommentCreateRequest {
        private Long articleId;
        private String content;
        private Long parentCommentId;
        private Long writerId;

    }




}
