package io.file;

import java.io.File;
import java.io.IOException;
import java.util.Date;

public class OldFileMain {

    public static void main(String[] args) throws IOException {
        File file = new File("temp/example.txt");
        File directory = new File("temp/exampleDir");

        // 1. exists(): 파일이나 디렉토리의 존재 여부를 확인
        System.out.println("File exists: " + file.exists());

        // 2. createNewFile(): 새 파일을 생성
        boolean created = file.createNewFile();
        System.out.println("File created: " + created);

        // 3. mkdir(): 새 디렉토리를 생성
        boolean dirCreated = directory.mkdir();
        System.out.println("Directory created: " + dirCreated);

        // 4. delete(): 파일이나 디렉토리를 삭제
        //boolean deleted = file.delete();
        //System.out.println("File deleted: " + deleted);

        // 5. isFile(): 파일인지 확인
        System.out.println("Is file: " + file.isFile());

        // 6. isDirectory(): 디렉토리인지 확인
        System.out.println("Is directory: " + directory.isDirectory());

        // 7. getName(): 파일이나 디렉토리의 이름을 반환
        System.out.println("File name: " + file.getName());

        // 8. length(): 파일의 크기를 바이트 단위로 반환
        System.out.println("File size: " + file.length() + " bytes");

        // 9. renameTo(File dest): 파일의 이름을 변경하거나 이동
        File newFile = new File("temp/newExample.txt");
        boolean renamed = file.renameTo(newFile);
        System.out.println("File renamed: " + renamed);

        // 10. lastModified(): 마지막으로 수정된 시간을 반환
        long lastModified = newFile.lastModified();
        System.out.println("Last modified: " + new Date(lastModified));
    }
}