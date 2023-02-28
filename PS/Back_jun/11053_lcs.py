'''
6
10 20 10 30 20 50
'''
import bisect
def play(lst):
    dp = [1]*(n)
    for i in range(1,n):
        mx_idx = 0
        for j in range(mx_idx,i):
            if lst[j]<lst[i] and dp[j]+1 > dp[i]: # 즉 그전에 자기보다 작은 것이 없다는 뜻
                dp[i]=dp[j]+1
                mx_idx = j
    return max(dp)
n = int(input())
lst = list(map(int,input().split()))
print(play(lst))

# + 이분탐색
# 교체해주는 이유 => 다음 수와 비교해야하기 때문
# 따라서 숫자를 세주는 것만 가능하다
def bi(lst):
    stack =[0]
    for l in lst:
        # l 이 현재 가장 큰 수라면 append
        if stack[-1]<l:
            stack.append(l)

        # l이 현재 가장 큰수가 아니거나 같은 수라면
        else:
            # l보다 작거나 같은 수 중 최댓값을 찾아서 교체
            # 이유? => 다음 수와 비교할때 교체된 것으로 비교 해주어야하기 때문
            # 따라서 append같이 추가를 해줄순 없고 교체만 가능하다
            stack[bisect.bisect_left(stack,l)]=l
    return len(stack)-1

print(bi(lst))


# 원래 코드
def original(lst):
    dp = [1]*(n)
    for i in range(1,n):
        for j in range(i):
            if lst[j]<lst[i]: # 즉 그전에 자기보다 작은 것이 없다는 뜻
                dp[i]=max(dp[j]+1,dp[i])
    return max(dp)