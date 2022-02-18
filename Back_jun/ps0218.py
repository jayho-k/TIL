'''
0218 라이브강의 문제풀이

- 문제풀이 단계

1. 문제 읽기
    (처음엔 흐름만 파악)
    (제약 조건은 체크하고 적어놓는다)
    (TC를 손으로 풀기)

2. 접근방법 구상
    사람의 방법 x
    arr, 반복, 조건으로 생각해본다

3. 핵심코드 손코딩
    반드시 시각적으로(arr, 범위, 반복) 푼다
    
4. 코드구현

5. 디버깅 및 개선
    디버깅을 하기 전에는 문제를 다시 읽어봐야한다

'''

# 1 현주문제
# 인덱스 직관적으로 짜기 = 인덱스와 일치시키자
# 실수를 줄일 수 있는 형태로
# 1을 하나 추가해주는 정도

T = int(input())
for tc in  range(1,T+1):
    n, q = map(int, input().split())
    lst = [0]*(n+1) 

    for q1 in range(1, q+1):
        l, r = map(int, input().split())
        for i in range(l, r+1):
            lst[i] = q1


    ans = ' '.join(map(str,lst[1:]))
    print(f'#{tc} {ans}')


















