# 08_Strategy



- **동일한 틀 안**에 있는 **특정 작업의 방식, 모드**를 바꿔줄때 사용한다.
- Search 여러 버튼이 있을 경우



## 예제 (Search 여러 버튼이 있을 경우)

> Main.java

```java
package strategy.after;

public class Main {
  public static void main(String[] args) {
    MyProgram myProgram = new MyProgram();
    myProgram.testProgram();
  }
}
```



> MyProgram.java

```java
public class MyProgram{
    
    private SearchButton searchButton = new SearchButton(this);
    
    public void setModeAll(){
        searchButton.setSearchStrategy(new SearchStrategyAll());
    }
    
    public void setModeImage(){
        searchButton.setSearchStrategy(new SearchStrategyImage());
    }
    
    public void setModeNews(){
        searchButton.setSearchStrategy(new SearchStrategyNews());
    }
    
    public void setModeMap(){
        searchButton.setSearchStrategy(new SearchStrategyMap());
    }
    
    public void testProgram(){
        searchButton.onClick();
        
        // 이미지 setting => 클릭
        setmodeImage();
        searchButton.onClick();
        
        // 뉴스 setting => 클릭
        setmodeNews();
        searchButton.onClick();
		
        // 버튼 setting => 클릭
        setmodeMap();
        searchButton.onClick();
    }
}
```



> SearchStrategy.java

```java
package strategy.after;

interface SearchStrategy {
  public void search ();
}

class SearchStratagyAll implements SearchStrategy {
  public void search () {
      System.out.println("SEARCH ALL");
      // 전체검색하는 코드
  }
}

class SearchStratagyImage implements SearchStrategy {
  public void search () {
      System.out.println("SEARCH IMAGE");
      // 이미지검색하는 코드
  }
}

class SearchStratagyNews implements SearchStrategy {
  public void search () {
      System.out.println("SEARCH NEWS");
      // 뉴스검색하는 코드
  }
}

class SearchStratagyMap implements SearchStrategy {
  public void search () {
      System.out.println("SEARCH MAP");
      // 지도검색하는 코드
  }
}
```



> SearchButton.java

```java
package strategy.after;

public class SearchButton {

  private MyProgram myProgram;

  public SearchButton (MyProgram _myProgram) {
    myProgram = _myProgram;
  }

  private SearchStrategy searchStrategy = new SearchStratagyAll();
  
  public void setSearchStrategy (SearchStrategy _searchStrategy) {
    searchStrategy = _searchStrategy;
  }

  public void onClick () {
    searchStrategy.search();
  }
}
```
