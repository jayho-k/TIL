# 07_State



TV를 누르면 켜지고 켜져있으면 꺼지는 패턴을 만들때 사용



> MyProgram.java

```java
package state;

public class MyProgram {
  public static void main(final String[] args) {
    final ModeSwitch modeSwitch = new ModeSwitch();

    modeSwitch.onSwitch(); // "FROM LIGHT TO DARK" 출력
    modeSwitch.onSwitch(); // "FROM DARK TO LIGHT" 출력
    modeSwitch.onSwitch(); // "FROM LIGHT TO DARK" 출력
    modeSwitch.onSwitch(); // "FROM DARK TO LIGHT" 출력
  }
}
```



> ModeState.java

```java
public interface ModeState{
    public void toggle (ModeSwitch modeSwitch);
}

class ModeStateLight implements ModeState{
    public void toggle (ModeSwitch modeSwitch){
        System.out.println("light => dark");
        modeSwitch.setState(new ModeStateDark());
    }
}

class ModeStateDark implements ModeState{
    public void toggle (ModeSwitch modeSwitch){
        System.out.println("dark => light");
        modeSwitch.setState(new ModeStateLight());
    }
}
```



> ModeStitch.java

```java
public class ModeSwitch{
    private ModeState modeState = new ModeStateLight();
    
    public void setState(ModeState _modeState){
        modestate = _modeState;
    }
    
    public void onSwitch(){
        modeState.toggle(this);
    }
}
```























