# 03_FunctionSetting





### 외부 Application metric 수집하기

- 어디라도 /metrics만 있으면 사용가능하다.

**실습**

- 다른 외부 Application을 띄워서 metric을 수집하는 것을 목표로 한다.

![image-20260104174851373](./03_FunctionSetting.assets/image-20260104174851373.png)

- harhor 라는 appication의 yaml 확인

- 위와 같이 metric이라는 부분을 설정해준다.

- http://192.168.1.63:9090/metrics

  - <img src="./03_FunctionSetting.assets/image-20260104175344381.png" alt="image-20260104175344381" style="zoom:67%;" />
  - 이렇게 하면 /metrics로 해당 부분의 metrics가 노출되었다는 것을 확인 할 수 있다.

- 이제 prometheus에 yaml로 값을 job을 추가하게 된다.

  - ![image-20260104175516219](./03_FunctionSetting.assets/image-20260104175516219.png)
  - 이렇게 targets을 고정으로 등록해주게 되고 metrics_path를 등록해준다.

- Patch 시작해야함

  - 

  - ```docker
    k patch configmap -n monitoring prometheus-server --patch-f
    ile 4.add-harbor-to-the-prometheus.yaml   
    ```

