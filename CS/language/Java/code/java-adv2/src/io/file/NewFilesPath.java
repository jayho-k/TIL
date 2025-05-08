package io.file;

import java.io.IOException;
import java.nio.file.Files;
import java.nio.file.Path;
import java.util.List;
import java.util.stream.Stream;

public class NewFilesPath {

    public static void main(String[] args) throws IOException {
        Path path = Path.of("temp/..");
        System.out.println("path = " + path);

        // 절대 경로
        System.out.println("Absolute path = " + path.toAbsolutePath());
        // 정규 경로
        System.out.println("Canonical path = " + path.toRealPath());

        Stream<Path> pathStream = Files.list(path);
        List<Path> list = pathStream.toList();
        pathStream.close();

        for (Path p : list) {
            System.out.println( (Files.isRegularFile(p) ? "F" : "D") + " | " + p.getFileName());
        }
    }
}
