# 투포인터

백준 2003 문제

1 2 3 4 2 5

- 이런식으로 lst가 존재
- 포인트 start, end를 인덱스 1에 지정
- 내가 생각한 값보다 커?   ==> end 앞으로 1보
- 내가 생각한 값보다 작아?   ==> start 앞으로 1보
- 그렇게 한번 쓱 훓는 것임
- 이것은 O(n)임 ==> 개꿀

```python
'''
투포인터를 이용할 것이다
부분합 = area_num
area_num >= m ==> st+=1  ==> 스타트 부분만 빼주면 된다.
area_num >= m ==> end += 1 ==>  end부분만 더해주면 된다
'''

n, m = map(int, input().split())
lst = list(map(int, input().split()))
area_sum = 0
end = 0
cnt = 0
for st in range(n):

    while area_sum < m and end < n:

        area_sum += lst[end]
        end += 1

    if area_sum == m:
        cnt += 1

    area_sum -= lst[st]

print(cnt)
```

