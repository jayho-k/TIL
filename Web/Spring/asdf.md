# EnableConfigurationProperties



## 🔄 **3️⃣ @EnableConfigurationProperties의 작동 타이밍**

1. **SpringApplication 초기화**
   - `SpringApplication.run()`이 호출됩니다.
2. **prepareEnvironment 단계**
   - `ConfigDataEnvironmentPostProcessor`가 `application.yml`을 로드하여 `PropertySource`로 `Environment`에 저장합니다.
3. **ApplicationContext 생성 전**
   - `ApplicationContext`가 생성되기 직전에 `@EnableConfigurationProperties`가 처리됩니다.
   - 이 단계에서 `ConfigurationPropertiesBindingPostProcessor`가 등록됩니다.
4. **ApplicationContext 초기화**
   - `ConfigurationPropertiesBindingPostProcessor`가 `@ConfigurationProperties` 클래스를 감지하고 빈으로 등록합니다.
   - `Binder`가 `Environment`의 값을 해당 클래스 필드에 바인딩합니다.
5. **ApplicationContext 완성**
   - 최종적으로 `@ConfigurationProperties` 빈이 `ApplicationContext`에 등록되고 사용할 준비가 됩니다.



## 📊 **4. Environment에 값 저장**

`application.yml`에서 읽어온 값들은 **Environment 객체**에 `PropertySource` 형태로 저장됩니다.

예를 들어:





