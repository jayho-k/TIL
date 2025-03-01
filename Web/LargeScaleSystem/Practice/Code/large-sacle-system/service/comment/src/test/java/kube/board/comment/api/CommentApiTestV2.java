package kube.board.comment.api;


import kube.board.comment.service.request.CommentCreateRequestV2;
import kube.board.comment.service.response.CommentPageResponse;
import kube.board.comment.service.response.CommentResponse;
import lombok.AllArgsConstructor;
import lombok.Getter;
import org.junit.jupiter.api.Test;
import org.springframework.core.ParameterizedTypeReference;
import org.springframework.web.client.RestClient;

import java.util.List;

public class CommentApiTestV2 {

    RestClient restClient = RestClient.create("http://localhost:9001");

    @Test
    void create(){
        CommentResponse response1 = create(new CommentCreateRequestV2(1L, "my comment1", null, 1L));
        CommentResponse response2 = create(new CommentCreateRequestV2(1L, "my comment2", response1.getPath(), 1L));
        CommentResponse response3 = create(new CommentCreateRequestV2(1L, "my comment3", response2.getPath(), 1L));


        System.out.println("path 1 = " + response1.getPath());
        System.out.println("commentId 1 = " + response1.getCommentId());
        System.out.println("\tpath 2 = " + response2.getPath());
        System.out.println("\tcommentId 2 = " + response2.getCommentId());
        System.out.println("\t\tpath 3 = " + response3.getPath());
        System.out.println("\t\tcommentId 3 = " + response3.getCommentId());

        /*
            path 1 = 00001
            commentId 1 = 154141949191835648
                path 2 = 0000100000
                commentId 2 = 154141949573517312
                    path 3 = 000010000000000
                    commentId 3 = 154141949661597696
        */

    }


    CommentResponse create(CommentCreateRequestV2 request) {
        return restClient.post()
                .uri("/v2/comments")
                .body(request)
                .retrieve()
                .body(CommentResponse.class);
    }

    @Test
    void read(){
        CommentResponse response = restClient.get()
                .uri("/v2/comments/{commentId}", 154141949191835648L)
                .retrieve()
                .body(CommentResponse.class);
        System.out.println("res = " + response);
    }

    @Test
    void delete(){
        restClient.delete()
                .uri("/v2/comments/{commentId}", 154141949191835648L)
                .retrieve();
    }


    @Test
    void readAll(){
        CommentPageResponse response = restClient.get()
                .uri("/v2/comments?articleId=1&page=1&pageSize=10")
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
        /*response.getCommentCount() = 101
            comment.getCommentId() = 154140839391580160
            comment.getCommentId() = 154140840708591616
            comment.getCommentId() = 154140840800866304
            comment.getCommentId() = 154141949191835648
            comment.getCommentId() = 154141949573517312
            comment.getCommentId() = 154141949661597696
            comment.getCommentId() = 154145155403931657
            comment.getCommentId() = 154145155517177857
            comment.getCommentId() = 154145155517177867
            comment.getCommentId() = 154145155517177884
        */
    }

    @Test
    void readAllInfiniteScroll() {
        List<CommentResponse> response1 = restClient.get()
                .uri("/v2/comments/infinite-scroll?articleId=1&pageSize=5")
                .retrieve()
                .body(new ParameterizedTypeReference<List<CommentResponse>>() {
                });

        System.out.println("firstPage");
        for (CommentResponse comment : response1) {
            // comment id 가 자기 자신이 아니면 depth를 가지고 있다는 뜻
            System.out.println("comment.getCommentId() = " + comment.getCommentId());
        }

        String lastPath = response1.getLast().getPath();


        System.out.println("secondPage");

        List<CommentResponse> response2 = restClient.get()
                .uri("/v2/comments/infinite-scroll?articleId=1&pageSize=5&lastPath=%s"
                        .formatted(lastPath))
                .retrieve()
                .body(new ParameterizedTypeReference<List<CommentResponse>>() {
                });

        for (CommentResponse comment : response2) {
            System.out.println("comment.getCommentId() = " + comment.getCommentId());
        }

        /*
          firstPage
            comment.getCommentId() = 154140839391580160
            comment.getCommentId() = 154140840708591616
            comment.getCommentId() = 154140840800866304
            comment.getCommentId() = 154141949191835648
            comment.getCommentId() = 154141949573517312
          secondPage
            comment.getCommentId() = 154141949661597696
            comment.getCommentId() = 154145155403931657
            comment.getCommentId() = 154145155517177857
            comment.getCommentId() = 154145155517177867
            comment.getCommentId() = 154145155517177884
        */
    }

    @Getter
    @AllArgsConstructor
    public static class CommentCreateRequest {
        private Long articleId;
        private String content;
        private Long parentPath;
        private Long writerId;

    }




}
