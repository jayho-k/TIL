# 05_Kubeflow



## 05_1) AI 과정

> - 일반적인 모습

<img src="./05_Kubeflow.assets/image-20230726140051428.png" alt="image-20230726140051428" style="zoom:67%;" />

- 실험 단계

  1. 문제 정의, 데이터 수집 및 분석 

  2. ML model 선택

  3. 실험 및 training

  4. 하이퍼파라미터 튜닝

     

- 배포 과정

  1. data 변형
  2. train model
  3. model serving
  4. monitoring

Kubeflow는 위 과정들을 K8s를 바탕으로 진행할 수 있게 도와주는 툴이다.



## 05_2) kubeflow 란?

<img src="./05_Kubeflow.assets/image-20230726140652061.png" alt="image-20230726140652061" style="zoom:80%;" />

- 위와 같은 서비스들을 제공한다.
- 머신러닝 workflow의 ML model 학습부터 배포단계까지 모든 작업에 필요한 도구와 환경을 K8s위에서 component로 제공한다. 
- Compoenet
  - Central Dashboard : Notebooks, AutoML, KFP등의 컴포넌트를 이용할 수 있도록 UI를 제공
  - Training Operrators
    - 딥러닝 프레임워크에 대해 분산 학습을 지원한다.
    - 사용자가 분산 학습 명세서를 작성하여 K8s에 배포하면 Kubeflow Training Operator는 명세서에 따라 workflow를 실행한다.
  - Kaib
    - Kaib를사용하여 AutoML 기능을 제공한다.
    - Hyper Parameter Tuning, Neural Architecture Search기능이 있다.
  - Pipelines
    - 머신러닝 workflow를 구축하고 배포하기 위한 ML Workflow Orchestration 도구
    - Pipelines와 Pipeline Components를 재사용하여 다양한 실험을 빠르고 쉽게 수행할 수 있음
    - 머신러닝 workflw를 DAG(방향 순환이 없는 그래프)로 정의한 것
    - model을 serving까지 보내는데 필요한 모든 작업을 재사용 가능한 단위(component)로 나누고, k8s위에서 연결시켜주는 역할













wget -Uri https://github.com/kubernetes-sigs/kustomize/releases/download/kustomize%2Fv5.0.3/kustomize_v5.0.3_windows_amd64.tar.gz -OutFile kustomize_v5.0.3_windows_amd64.tar.gz



```
tar -xvzf C:\Users\jayho\Desktop\mlops-prac\kubeflow-prac/kustomize_v5.0.3_windows_amd64.tar.gz -C C:\Users\jayho\Desktop\mlops-prac\kubeflow-prac/kustomize_v5.0.3_windows_amd64
```



minikube start --driver=docker --cpus=4 --memory=6g --kubernetes-version=v1.25.11



 --extra-config=apiserver.service-account-signing-key-file=/var/lib/minikube/certs/s a.key --extra-config=apiserver.service-account-issuer=kubernetes.default.svc







- `Kubernetes` (up to `1.26`) with a default StorageClass

- ```
  kustomize
  ```

  5.0.3

  - ⚠️ Kubeflow is not compatible with earlier versions of Kustomize. This is because we need the [`sortOptions`](https://kubectl.docs.kubernetes.io/references/kustomize/kustomization/sortoptions/) field, which is only available in Kustomize 5 and onwards [#2388](https://github.com/kubeflow/manifests/issues/2388).

- `kubectl`



1.25.11





Overview

![image-20230726142752532](./05_Kubeflow.assets/image-20230726142752532.png)





