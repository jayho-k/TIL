# Hash Map

맵(Map) 인터페이스의 해시 테이블 기반 구현입니다. 이 구현은 맵의 모든 선택적 연산을 제공하며, `null` 값과 `null` 키를 허용합니다. (`HashMap` 클래스는 대체로 `Hashtable`과 동등하지만, 동기화되어 있지 않고 `null`을 허용한다는 점에서 다릅니다.) 이 클래스는 맵의 순서를 보장하지 않습니다. 특히, 시간이 지나도 순서가 일정하게 유지된다는 보장이 없습니다.

이 구현은 기본 연산들(`get`과 `put`)에 대해 **상수 시간 성능**을 제공합니다. 단, 해시 함수가 요소들을 버킷에 잘 분산시킨다는 가정 하에서입니다. 컬렉션 뷰(collection views)를 통한 반복(iteration)은 `HashMap` 인스턴스의 **"용량"(버킷의 수)**과 그 **크기(키-값 매핑의 수)**에 비례하는 시간이 필요합니다. 따라서 반복 성능이 중요할 경우, 초기 용량을 너무 크게 설정하거나 부하율(load factor)을 너무 낮게 설정하지 않는 것이 매우 중요합니다.

`HashMap` 인스턴스는 성능에 영향을 미치는 두 가지 매개변수를 갖습니다: **초기 용량(initial capacity)**과 **부하율(load factor)**입니다. 용량(capacity)은 해시 테이블 내의 버킷 수이고, 초기 용량은 해시 테이블이 생성될 때의 용량을 의미합니다. 부하율은 해시 테이블이 얼마나 차 있어도 되는지를 나타내는 척도입니다. 테이블에 저장된 항목 수가 `(현재 용량 × 부하율)`을 초과하게 되면, 해시 테이블은 재해싱(rehash)되어 내부 데이터 구조가 재구성되며, 대략 두 배의 버킷을 가지게 됩니다.

일반적으로, 기본 부하율인 `0.75`는 시간과 공간 비용 사이에서 좋은 균형을 제공합니다. 부하율을 높이면 공간 오버헤드는 줄어들지만, 조회 비용(`get`, `put` 등의 연산에 반영됨)은 증가합니다. 기대되는 맵의 항목 수와 부하율을 고려하여 초기 용량을 설정하면 재해싱(rehash) 횟수를 최소화할 수 있습니다. 만약 초기 용량이 `(최대 항목 수 ÷ 부하율)`보다 크다면, 재해싱은 발생하지 않습니다.

많은 매핑이 `HashMap` 인스턴스에 저장될 예정이라면, 자동으로 테이블을 확장하면서 재해싱을 수행하는 것보다, 충분히 큰 용량으로 인스턴스를 생성하는 것이 훨씬 효율적입니다. 동일한 `hashCode()`를 가진 많은 키를 사용하는 것은 어떤 해시 테이블에서도 성능을 느리게 만드는 확실한 방법입니다. 이러한 영향을 완화하기 위해, 키가 `Comparable`일 경우, 이 클래스는 키들 간의 비교 순서를 이용하여 충돌을 해결하려고 시도할 수 있습니다.

이 구현은 동기화되어 있지 않다는 점에 유의하십시오. 여러 스레드가 동시에 해시 맵에 접근하고, 그 중 하나라도 맵을 구조적으로 수정(structural modification)할 경우, 외부에서 동기화를 수행해야 합니다. (구조적 수정이란 하나 이상의 매핑을 추가하거나 삭제하는 연산이며, 이미 포함된 키에 대한 값 변경은 구조적 수정이 아닙니다.) 일반적으로, 맵을 자연스럽게 감싸는 어떤 객체에 대해 동기화를 수행하는 방식으로 처리됩니다. 만약 그런 객체가 없다면, 맵은 `Collections.synchronizedMap` 메서드를 사용하여 "래핑(wrap)"되어야 합니다. 이는 맵을 생성할 때 수행하는 것이 좋으며, 우발적인 비동기 접근을 방지할 수 있습니다:

```java
Map m = Collections.synchronizedMap(new HashMap(...));
```

이 클래스의 "컬렉션 뷰 메서드"들이 반환하는 반복자들은 **fail-fast**입니다. 반복자가 생성된 이후에, 반복자의 자체 `remove` 메서드를 제외한 어떤 방식으로든 맵이 구조적으로 수정되면, 반복자는 `ConcurrentModificationException`을 던집니다. 따라서, 동시 수정 상황에서 반복자는 임의적이고 비결정적인 행동을 하도록 내버려두는 대신, **빠르고 명확하게 실패**합니다.

그러나, 반복자의 fail-fast 동작은 **보장할 수 없습니다**. 일반적으로, 동기화되지 않은 동시 수정 상황에서는 어떤 확실한 보장을 제공하는 것은 불가능하기 때문입니다. fail-fast 반복자는 가능한 최선의 노력(best-effort basis)으로 `ConcurrentModificationException`을 던집니다. 따라서 이 예외에 프로그램의 정확성을 의존하는 것은 잘못된 일입니다. 반복자의 fail-fast 동작은 오직 **버그를 감지하기 위한 용도**로만 사용해야 합니다.





## hash

```java
/**
 * key.hashCode()를 계산한 후, 높은 비트들을 낮은 비트에 퍼뜨립니다 (XOR 연산 사용).
 * 해시 테이블은 2의 제곱수 크기의 마스킹을 사용하기 때문에,
 * 현재 마스크로 가려지는 비트보다 높은 비트만 다른 해시들은
 * 항상 충돌하게 됩니다.
 * (예를 들어, 작은 테이블에서 연속된 정수를 가진 Float 키 집합들이 해당됩니다.)
 * 따라서, 이러한 높은 비트의 영향을 낮은 쪽으로 퍼뜨리는 변환을 적용합니다.
 *
 * 여기에는 속도, 유용성, 비트 분산 품질 사이의 균형이 존재합니다.
 * 많은 일반적인 해시 집합은 이미 꽤 잘 분포되어 있기 때문에
 * 굳이 이 퍼뜨리기 과정이 큰 도움이 되지 않을 수도 있으며,
 * 해시 버킷 안에서 충돌이 많은 경우 트리(Tree)를 사용해서 처리하기 때문에,
 * 단순한 XOR 방식으로 가장 저렴하게 비트 손실을 줄이고,
 * 테이블 크기 제한 때문에 원래는 인덱스 계산에 사용되지 않는 높은 비트의 영향도
 * 포함하도록 합니다.
 */

static final int hash(Object key) {
    int h;
    // hashCode = 스레드 
    // 16을 오른쪽으로 시프트 하는 이유는 상위비트와 하위비트를 섞어서 key값이 조금더 
    // 분산될 수 있게끔 하기 위해서다
    return (key == null) ? 0 : (h = key.hashCode()) ^ (h >>> 16);
}
```

예제 9에서 볼 수 있는 것처럼, Java 8 HashMap 보조 해시 함수는 상위 16비트 값을 XOR 연산하는 매우 단순한 형태의 보조 해시 함수를 사용한다. 이유로는 두 가지가 있는데, 첫 번째는 Java 8에서는 해시 충돌이 많이 발생하면 링크드 리스트 대신 트리를 사용하므로 해시 충돌 시 발생할 수 있는 성능 문제가 완화되었기 때문이다. 두 번째로는 최근의 해시 함수는 균등 분포가 잘 되게 만들어지는 경향이 많아, Java 7까지 사용했던 보조 해시 함수의 효과가 크지 않기 때문이다. 두 번째 이유가 좀 더 결정적인 원인이 되어 Java 8에서는 보조 해시 함수의 구현을 바꾸었다.

개념상 해시 버킷 인덱스를 계산할 때에는 index = X.hashCode() % M처럼 나머지 연산을 사용하는 것이 맞지만, M값이 2a일 때는 해시 함수의 하위 a비트 만을 취한 것과 값이 같다. 따라서 나머지 연산 대신 '1 << a – 1' 와 비트 논리곱(AND, &) 연산을 사용하면 수행이 훨씬 더 빠르다.



```java
@IntrinsicCandidate
public native int hashCode();
```

- 동일한 애플리케이션 실행 중에 동일한 객체에 대해 hashCode()를 여러 번 호출하면,
  equals() 비교에 사용되는 정보가 변경되지 않는 한 항상 같은 정수 값을 반환해야 합니다.
- 두 객체가 equals() 메서드에 따라 동일하다면,
  두 객체 각각에 대해 hashCode()를 호출했을 때 같은 해시 값을 반환해야 합니다.



```java
final V putVal(int hash, K key, V value, boolean onlyIfAbsent, 0boolean evict) {
    // 해시 테이블(tab), Node(p), 배열 길이(n), 인덱스(i)
    Node<K,V>[] tab; Node<K,V> p; int n, i; 
	
    // 아직 테이블이 없거나 길이가 0이면 resize()를 호출해 초기화
    if ((tab = table) == null || (n = tab.length) == 0)
        n = (tab = resize()).length;
    
    // (n - 1) & hash로 인덱스를 계산해서 인덱스가 비어있으면 새 노드로 채운다.
    if ((p = tab[i = (n - 1) & hash]) == null)
        tab[i] = newNode(hash, key, value, null);
    
    // 인덱스가 있으면? collision
    // p는 tab에 이미 존재하는 Node
    else {
        Node<K,V> e; K k;
		
        // p.hash == hash : 해쉬 값이 같고 --> 해쉬값이 다를수 있나?
        // (k = p.key) == key :  tab에 이미 존재하는 Node (첫번째)의 key와 동일한 경우
        // (key != null && key.equals(k)) : 
        //   key가 null이 아니고, key랑 equals인 경우 // key가 객체일 수도 있기 때문 
        if (p.hash == hash && ((k = p.key) == key || (key != null && key.equals(k))))
            e = p;
        // p가 TreeNode인 경우 => putTreeVal로 값을 넣음
        else if (p instanceof TreeNode)
            e = ((TreeNode<K,V>)p).putTreeVal(this, tab, hash, key, value);
        
        // hash가 다르거나 값이 다른 경우
        else {
            // 
            for (int binCount = 0; ; ++binCount) {
                // 끝 노드까지 도달
                if ((e = p.next) == null) {
                    // 새로운 노드를 생성
                    p.next = newNode(hash, key, value, null);
                    // TREEIFY_THRESHOLD = 8
                    // binCount가 8이상이면 treeifyBin으로 tree로 변환
                    if (binCount >= TREEIFY_THRESHOLD - 1) // -1 for 1st
                        treeifyBin(tab, hash);
                    break;
                }
                // hash가 같고, key가 같은(equals or ==) 노드를 찾았을 경우
                if (e.hash == hash &&
                    ((k = e.key) == key || (key != null && key.equals(k))))
                    break;
                p = e;
            }
        }
        // 끝 노드까지 도달하지 않아서 null이 아닌 경우
        // 즉 충돌 되었지만 완전 새로운 애는 아닌 경우 ==> update해줘야죠?
        if (e != null) { // existing mapping for key
            // 
            V oldValue = e.value;
            // onlyIfAbsent가 false이거나 이전에 존재하건 값이 null이면 
            if (!onlyIfAbsent || oldValue == null)
                // 값 갱신
                e.value = value;
            // 확인 필요!!!!
            afterNodeAccess(e);
            // old 값 return
            return oldValue;
        }
    }
    // HashMap이 구조적으로 수정된 횟수
    // HashMap 내의 매핑 수를 변경하거나, 내부 구조(예: 재해싱 등)를 수정하는 작업을 의미합니다.
    // Collection-view에서 생성된 반복자(iterator)들이 fail-fast 동작을 하도록 하기 위해 사용
    // ConcurrentModificationException 참고
    ++modCount;
    
    // 임계점(threshold) 보다 size가 초과 된다면 resize 시도
    if (++size > threshold)
        resize();
    // 확인 필요!!!!
    afterNodeInsertion(evict);
    return null;
}
```





##  Resize

- threshold가 뭐지?
- 

```java
/**
 * 테이블 크기를 초기화하거나 두 배로 확장합니다.
 * 테이블이 null이면, threshold 필드에 저장된 초기 용량 목표에 따라 테이블을 할당합니다.
 * 그렇지 않으면, 2의 거듭제곱 방식으로 확장되기 때문에 각 버킷에 있는 요소는
 * 기존 인덱스에 그대로 남거나, 새 테이블에서 2의 거듭제곱만큼 이동해야 합니다.
 *
 * @return 테이블 (배열)
*/

final Node<K,V>[] resize() {
    Node<K,V>[] oldTab = table; // oldTab = 기존 table    
    int oldCap = (oldTab == null) ? 0 : oldTab.length; // 이전 table 길이
    int oldThr = threshold; // 이전 resize 임계값
    int newCap, newThr = 0; // 새로운 용량, 임계값 초기화
    
    // 기존 테이블이 존재 할 경우
    if (oldCap > 0) {
        // 1 << 30 = 1,073,741,824
        if (oldCap >= MAXIMUM_CAPACITY) {
            // 이전oldCap이 최대가 넘어가면 threshold는 Integer.MAX_VALUE로 설정
            // 더이상 확장하지 않음
            threshold = Integer.MAX_VALUE; 
            return oldTab;
        }
        // oldCap을 약 2배늘린게 max보다 작고 oldCap이 default보다 크다면
        // 즉 기존 용량 2배, 새 임계값 2배로 늘림
        else if ((newCap = oldCap << 1) < MAXIMUM_CAPACITY &&
                 oldCap >= DEFAULT_INITIAL_CAPACITY)
            newThr = oldThr << 1; // double threshold
    }
    
    // 기존 테이블 용량이 없는데 이전 threshold가 설정된 상태라면?
    // 기존 테이블은 만들어져있는데 remove로 삭제된 경우인가?
    else if (oldThr > 0) // initial capacity was placed in threshold
        // 이전 값을 newCap으로 사용한다.
        newCap = oldThr;
    
    // 완전 처음인 경우
    else {               // zero initial threshold signifies using defaults
        // default, 
        newCap = DEFAULT_INITIAL_CAPACITY; // 1 << 4; // aka 16
        newThr = (int)(DEFAULT_LOAD_FACTOR * DEFAULT_INITIAL_CAPACITY); //  0.75f * 16 = 12
    }
    
    // 1. 기존 테이블이 존재, but newCap이 최대용량을 넘을 때, old가 default보다 작을 때
    // 2. 기존 테이블은 만들어져 있는데 remove로 삭제 되어서 Cap이 없을 경우
    if (newThr == 0) {
        // loadFactor랑 newCap기준으로 Threshold를 생성
        float ft = (float)newCap * loadFactor;
        newThr = (newCap < MAXIMUM_CAPACITY && ft < (float)MAXIMUM_CAPACITY ?
                  (int)ft : Integer.MAX_VALUE);
    }
    // 새 테이블에 할당
    threshold = newThr; // 초기화
    @SuppressWarnings({"rawtypes","unchecked"})
    Node<K,V>[] newTab = (Node<K,V>[])new Node[newCap]; // 새 테이블 생성
    table = newTab;
	    
    if (oldTab != null) {
        // 옛날 table 순회
        for (int j = 0; j < oldCap; ++j) {
            Node<K,V> e;
            // 순회 동안에 버킷에 값이 있을 경우
            if ((e = oldTab[j]) != null) {
                oldTab[j] = null; // 옛날건 비워주고
                
                // 연결리스트가 없는 단일 노드라면 새 테이블의 인덱스에 직접 배치
                if (e.next == null)
                    newTab[e.hash & (newCap - 1)] = e; // hash값 And (새로운 값-1) 확인 필요!!!
                
                // tree 구조라면 해당 split을 사용해서 재배치
                else if (e instanceof TreeNode)
                    ((TreeNode<K,V>)e).split(this, newTab, j, oldCap);
                
                // linked list라면
                // 각 기존 버킷의 Node들을 두 그룹으로 나누어 새로운 인덱스에 재배치하는 과정
                // 인덱스 재계산 : (e.hash & (newCap-1))
                // 성능 최적화를 위해 새로운 index는 기존 index 그대로거나,
                // 기존 index + oldCap이 됩니다.
                else { // preserve order
                    // lo
                    // hi
                    Node<K,V> loHead = null, loTail = null;
                    Node<K,V> hiHead = null, hiTail = null;
                    Node<K,V> next;
                    
                    do {
                        next = e.next;
                     //성능 최적화: rehash 과정에서 hash % newCapacity 
                     //            대신 비트 연산으로 빠르게 이동 여부 판단.

					// bucket 재정렬 최소화: 2배 확장시
                      //                    , 대부분은 그대로 두고 일부만 위치 바꿉니다.
                        
                        // lo 쪽으로 유지 (대부분은 lo쪽에 유지) 
                        if ((e.hash & oldCap) == 0) {
                            // lo Tail, head 초기화
                            if (loTail == null) // 처음 추가되는 노드
                                loHead = e; 
                            else // linked로 연결
                                loTail.next = e;
                            // Tail 초기화
                            loTail = e;
                        }
                        // hi 쪽으로 이동 (and가 0이 아니려면 둘다 1이어야 0이 아님)
                        else {
                            if (hiTail == null)
                                hiHead = e;
                            else
                                hiTail.next = e;
                            hiTail = e;
                        }
                     // next가 없을 때 까지 반복
                    } while ((e = next) != null);
                    
                    // 
                    if (loTail != null) {
                        loTail.next = null;
                        newTab[j] = loHead; // 기존 유지
                    }
                    if (hiTail != null) {
                        hiTail.next = null;
                        newTab[j + oldCap] = hiHead;  // old size만큼 ++ >> 이동
                    }
                }
            }
        }
    }
    return newTab;
}
```





### treeifyBin

```java
final void treeifyBin(Node<K,V>[] tab, int hash) {
        int n, index; Node<K,V> e;
    	// table의 크기가 64보다 작을 때 => resize를 먼저 시킴
        if (tab == null || (n = tab.length) < MIN_TREEIFY_CAPACITY)
            resize();
    	// 값도 충분히 클 경우
    	// 해당 index에 실제 값이 있는 경우 -> treeify 시작
        else if ((e = tab[index = (n - 1) & hash]) != null) {
            TreeNode<K,V> hd = null, tl = null;
            do {
                // Node >> TreeNode로 변환
                TreeNode<K,V> p = replacementTreeNode(e, null);
                if (tl == null)
                    hd = p;
                else {
                    p.prev = tl;
                    tl.next = p;
                }
                tl = p;
            } while ((e = e.next) != null);
            // RedBlock Tree로 변환
            if ((tab[index] = hd) != null)
                hd.treeify(tab);
        }
    }
```











