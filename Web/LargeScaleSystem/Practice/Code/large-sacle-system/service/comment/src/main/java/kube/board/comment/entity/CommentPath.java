package kube.board.comment.entity;

import jakarta.persistence.Embeddable;
import jakarta.persistence.Embedded;
import lombok.AccessLevel;
import lombok.Getter;
import lombok.NoArgsConstructor;
import lombok.ToString;

@Getter
@ToString
@Embeddable
@NoArgsConstructor(access = AccessLevel.PROTECTED)
public class CommentPath {

    private String path;

    // 몇번째 index 인지 확인하고 1을 increase 할 때 사용하기 위함
    private static final String CHARSET = "0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz";
    private static final int DEPTH_CHUNK_SIZE = 5;
    private static final int MAX_DEPTH = 5;

    // MIN_CHUNK : 00000, MAX_CHUNK : zzzzz
    private static final String MIN_CHUNK = String.valueOf(CHARSET.charAt(0)).repeat(DEPTH_CHUNK_SIZE);
    private static final String MAX_CHUNK = String.valueOf(CHARSET.charAt(CHARSET.length()-1)).repeat(DEPTH_CHUNK_SIZE);

    public static CommentPath create(String path){
        if (isDepthOverflowed(path)){
            throw new IllegalStateException("depth overflow");
        }
        CommentPath commentPath = new CommentPath();
        commentPath.path = path;
        return commentPath;
    }

    private static boolean isDepthOverflowed(String path) {
        return calDepth(path) > MAX_DEPTH;
    }

    private static int calDepth(String path){
        // 25 / 5 = 5
        return path.length() / DEPTH_CHUNK_SIZE;
    }

    public int getDepth(){
        return calDepth(path);
    }

    public boolean isRoot(){
        return calDepth(path) == 1;
    }

    public String getParentPath(){
        // 00000 00000
        // 끝에 5개 잘라내면 parent path
        return path.substring(0, path.length() - DEPTH_CHUNK_SIZE);
    }

    public CommentPath createChildCommentPath(String descendantsTopPath){
        if (descendantsTopPath == null) {
            return CommentPath.create(path + MIN_CHUNK);
        }
        String childrenTopPath = findChildrenTopPath(descendantsTopPath);
        return CommentPath.create(increase(childrenTopPath));
    }

    private String findChildrenTopPath(String descendantsTopPath) {
        return descendantsTopPath.substring(0, (getDepth() +1) * DEPTH_CHUNK_SIZE);
    }

    private String increase(String path){
        // 00001 00000
        // 마지막 00000에서 1을 더함
        String lastChunk = path.substring(path.length() - DEPTH_CHUNK_SIZE);
        if (isChunkOverflowed(lastChunk)){
            throw new IllegalStateException("chunk overflowed");
        }

        int charsetLength = CHARSET.length();

        int value = 0;
        for (char ch : lastChunk.toCharArray()) {
            // 10진수로 변환하기 위한 공식
            // (자릿수) + char 의 값
            value = value * charsetLength + CHARSET.indexOf(ch);
        }

        value = value + 1;

        String result = "";
        for (int i=0; i<DEPTH_CHUNK_SIZE; i++){
            // value % charsetLength => 해당 char의 위치
            result = CHARSET.charAt(value % charsetLength) + result;
            value /= charsetLength;
        }

        return path.substring(0, path.length() - DEPTH_CHUNK_SIZE) + result;
    }

    private boolean isChunkOverflowed(String lastChunk) {
        return MAX_CHUNK.equals(lastChunk);
    }


}
