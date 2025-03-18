package springpjt.advanced.app.v0;

import lombok.RequiredArgsConstructor;
import org.springframework.stereotype.Repository;

@Repository
@RequiredArgsConstructor
public class OrderRepositoryV0 {
    public void save(String itemId){
        // 상품 ID가 ex로 넘어오면 exception 터뜨려라
        if (itemId.equals("ex")){
            throw new IllegalStateException("Exception");
        }
        sleep(1000); //주문하는데 1초정도 걸린다고 가정
    }

    private void sleep(int millis) {
        try{
            Thread.sleep(millis);
        } catch (InterruptedException e){
            e.printStackTrace();
        }
    }
}
