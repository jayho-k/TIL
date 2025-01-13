package thread.sync;

import java.util.concurrent.locks.Lock;
import java.util.concurrent.locks.ReentrantLock;

import static util.MyLogger.log;
import static util.ThreadUtils.sleep;

public class BankAccountV3 implements BankAccount{

    private int balance;

    private final Lock lock = new ReentrantLock();

    public BankAccountV3(int initialBalance){
        this.balance = initialBalance;
    }

    @Override
    public boolean withdraw(int amount) {

        log("거래 시작 : " + getClass().getSimpleName());

        lock.lock(); // lock을 걸면 try finally를 통해 unlock을 해준다.
        try{
            // 검증 단계
            log("[검증 시작] 출금액 : " + amount + " , 잔액 : " + balance);
            if(balance < amount){
                log("[검증 실패]");
                return false;
            }

            // 완료
            log("[검증 완료] 출금액 : " + amount + " , 잔액 : " + balance);
            sleep(1000);
            balance = balance - amount;
            log("[출금 완료] 출금액 : " + amount + " , 잔액 : " + balance);
            // == 실제 필요한 임계 영역 종료 ==
        }finally {
            lock.unlock(); // lock 해제
        }
        log("거래 종료 : " + getClass().getSimpleName());
        return true;
    }

    @Override
    public int getBalance() {
        lock.lock();
        try{
            return balance;
        }
        finally {
            lock.unlock();
        }
    }
}
