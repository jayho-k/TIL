# 06_Detorator



## Decorator 패턴이란?

- 객체를 다른 객체에 넣어 **기능을 추가하는 방식**

### 예제 (비행기 게임)

> DecoratorPattern.java

```java
public class DecoratorPattern{
    public static void main(String[] args){
        
        // 탄환 발사
        new XWingFinghter().attack();
        
        // 탄환 발사
        // 레이저 발사
        new LaserDecorator(new XWingFinghter()).attack();
        
        // 탄환 발사
        // 레이저 발사
        // 미사일 발사
        // 플라즈마 발사
        new PlasmaDecorator(
        	new MissileDecorator(
            	new LaserDecorator(
                    new XWingFinghter())).attack();
        
    }
}
```



> Fighter.java

```java
public interface Fighter{
    public void attack();
}
```



> XWingFighter.java

```java
public class XWingFighter implements Fighter{
    @Override
    public void attack(){
        System.out.println("탄환 발사");
    }
}
```



> FighterDecorator.java

```java
public abstract class FighterDecorator implements Fighter{
    
    private Fighter decoratedFighter;
    public FighterDecorator(FIghter _decoratedFighter){
        decoratedFighter = _decoratedFIghter;
    }
    
    @Override
    public void attack(){
       dcoratedFighter.attack();
    }
}
```



> LaserDecorator.java

```java
public class LaserDecorator extends FighterDecorator {
  public LaserDecorator (Fighter _decoratedFighter) {
    super(_decoratedFighter);
  }
    
  @Override
  public void attack () {
    super.attack();
    System.out.println("레이저 발사");
  }
}
```



> MissileDecorator.java

```java
public class MissileDecorator extends FighterDecorator {
  public MissileDecorator (Fighter _decoratedFighter) {
    super(_decoratedFighter);
  }
  @Override
  public void attack () {
    super.attack();
    System.out.println("미사일 발사");
  }
}
```



> PlasmaDecorator.java

```java
public class PlasmaDecorator extends FighterDecorator {
  public PlasmaDecorator (Fighter _decoratedFighter) {
    super(_decoratedFighter);
  }
  @Override
  public void attack () {
    super.attack();
    System.out.println("플라즈마 발사");
  }
}
```



## + Factory method 패턴



> FighterFactory.java

```java
public class FighterFactory{
    public Fighter getFighter(boolean laser, boolean middile, boolean plasma){
        Fighter fighter new XWingFighter();
        
        if (laser) fighter = new LaserDecorator(fighter));
        if (missile) fighter = new MissileDecorator(fighter));
        if (plasma) fighter = new plasmaDecorator(fighter));
        
        return fighter;
    }	
}
```



> FactoryDecorator.java

```java
public class FactoryDecorator {
  public static void main(String[] args) {
    FighterFactory factory = new FighterFactory();
    
    factory.getFighter(false, false, false).attack();
    // 탄환 발사

    factory.getFighter(true, false, true).attack();
    // 탄환 발사
    // 레이저 발사
    // 플라즈마 발사

    factory.getFighter(true, true, false).attack();
    // 탄환 발사
    // 레이저 발사
    // 미사일 발사

    factory.getFighter(true, true, true).attack();
    // 탄환 발사
    // 레이저 발사
    // 미사일 발사
    // 플라즈마 발사
  }
}
```
