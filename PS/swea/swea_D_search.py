'''
그냥 이진탐색

middle을 잡아주는 것이 중요

찾아야하는 페이지를 다들 받은 것 

cnt = ?


while strt < end: 스타트가 더 크다는 뜻은  end ~ s 이렇게 됐는 소리
    조건1
      a < middle  ==> 미들이 end
      a > middle  ==> 미들이 strt
      a = middle  ==> 찾았음

'''


T = int(input())
for tc in range(1, T+1):
    strt = 1
    end, a, b = map(int, input().split())
    end_b = end
    cnt_a = 0
    while strt < end:
        middle = (strt + end)//2

        if a < middle:
            end = middle

        elif a > middle:
            strt = middle

        elif a == middle:
            break
        cnt_a += 1

    strt = 1
    cnt_b = 0
    while strt < end_b:

        middle = (strt + end_b)//2

        if b < middle:
            end_b = middle

        elif b > middle:
            strt = middle

        elif b == middle:
            break
        
        cnt_b += 1

    if cnt_a < cnt_b:
        print(f'#{tc} A')

    elif cnt_a > cnt_b:
        print(f'#{tc} B')
    else:
        print(f'#{tc} 0')

