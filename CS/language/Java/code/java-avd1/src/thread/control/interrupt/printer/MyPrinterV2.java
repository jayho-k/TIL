package thread.control.interrupt.printer;

import java.util.Queue;
import java.util.Scanner;
import java.util.concurrent.ConcurrentLinkedQueue;

import static util.MyLogger.log;

public class MyPrinterV2 {

    public static void main(String[] args) {

        Printer printer = new Printer();
        Thread printerThread = new Thread(printer, "printer");
        printerThread.start();

        Scanner userInput = new Scanner(System.in);

        while (true){
            log("프린터할 문서를 입력하세요. 종료 (q): ");
            String input = userInput.nextLine();
            if(input.equals("q")){
                printerThread.interrupt();
                break;
            }
            printer.addJob(input);
        }

    }

    static class Printer implements Runnable {

        volatile boolean work = true; // 여러 스레드가 동시에 접근하는 변수에는 volatile 키워드를 붙여줘야 안전
        Queue<String> jobQueue = new ConcurrentLinkedQueue<>(); // 동시성 컬렉션을 사용해야한다.

        @Override
        public void run() {
            while(!Thread.interrupted()){
                if (jobQueue.isEmpty())
                    continue;
                try {
                    String job = jobQueue.poll();
                    log("출력 시작 : " + job + ", 대기 문서: " + jobQueue);
                    Thread.sleep(3000);
                    log("출력 종료");
                } catch (InterruptedException e) {
                    log("interrupt!");
                    break;
                }
            }
            log("printer 종료");
        }

        public void addJob(String input){
            jobQueue.offer(input);
        }

    }

}