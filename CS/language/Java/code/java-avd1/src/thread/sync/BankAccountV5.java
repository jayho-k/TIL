package thread.sync;

import java.util.concurrent.locks.Lock;
import java.util.concurrent.locks.ReentrantLock;

import static util.MyLogger.log;
import static util.ThreadUtils.sleep;

public class BankAccountV5 implements BankAccount{

    private int balance;

    private final Lock lock = new ReentrantLock();

    public BankAccountV5(int initialBalance){
        this.balance = initialBalance;
    }

    @Override
    public boolean withdraw(int amount) {

        log("거래 시작 : " + getClass().getSimpleName());

        if(!lock.tryLock()){ // lock 있으면 대기 하지 않을 거야
            log("[진입 실패] 이미 처리중인 작업이 있습니다.");
            return false;
        }

        lock.lock();
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
        }
        finally {
            lock.unlock();
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
