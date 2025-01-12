package thread.sync;

import static util.MyLogger.log;
import static util.ThreadUtils.sleep;

public class BankAccountV1 implements BankAccount{

    private int balance;

    public BankAccountV1(int initialBalance){
        this.balance = initialBalance;
    }

    @Override
    public synchronized boolean withdraw(int amount) {

        log("거래 시작 : " + getClass().getSimpleName());

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


        log("거래 종료 : " + getClass().getSimpleName());
        return true;
    }

    @Override
    public synchronized int getBalance() {
        return balance;
    }
}
