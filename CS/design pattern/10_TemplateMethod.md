# 10_TemplateMethod

- 작업을 처리하는 일부분을 서브 클래스로 캡슐화해서 전체 일을 수행하는 구조는 바꾸지 않으면서 특정 단계에서 수행하는 내역을 바꾸는 패턴
- ex_ **떡만드는 순서는 같음** but, 순서안에서 하는 방법이 다를 수 있음



> TemplateExample.java

```java
public class TemplateExample{
    public static void main(String[] args){
        new NaverMapView().initMap();
        new KaKaoMapView().initMap();
    }
}
```



> MapView.java

```java
public abstract class MapView{
    
    // 순서가 같지만 내부 동작이 다름
    protected abstract void connectMapServer();
    protected abstract void showMapOnScreen();
    protected abstract void moveToCurrentLocation();
	
    public void initMap(){
        connectMapServer();
        showMapOnScreen();
        moveToCurrentLocation();
    }
}
```



> NaverMapView.java

```java
public class NaverMapView extends MapView {

  @Override
  protected void connectMapServer() {
    System.out.println("네이버 지도 서버에 연결");
  };
  @Override
  protected void showMapOnScreen() {
    System.out.println("네이버 지도를 보여줌");
  };
  @Override
  protected void moveToCurrentLocation() {
    System.out.println("네이버 지도에서 현 좌표로 이동");
  };  
}
```



> KakaoMapView.java

```java
public class KakaoMapView extends MapView {

  @Override
  protected void connectMapServer() {
    System.out.println("카카오 지도 서버에 연결");
  };
  @Override
  protected void showMapOnScreen() {
    System.out.println("카카오 지도를 보여줌");
  };
  @Override
  protected void moveToCurrentLocation() {
    System.out.println("카카오 지도에서 현 좌표로 이동");
  };
}
```

