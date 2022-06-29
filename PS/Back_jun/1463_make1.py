'''
정수 X에 사용할 수 있는 연산은 다음과 같이 세 가지 이다.

X가 3으로 나누어 떨어지면, 3으로 나눈다.
X가 2로 나누어 떨어지면, 2로 나눈다.
1을 뺀다.
정수 N이 주어졌을 때, 위와 같은 연산 세 개를 적절히 사용해서 1을 만들려고 한다. 
연산을 사용하는 횟수의 최솟값을 출력하시오.

아이디어가 어떻게 생각났는지에 대해서 물어보기
'''
n = int(input())

dp = [0]*(n+1)

for i in range(2,n+1):
    
    twmok, twnamuzi = divmod(i,2)
    trimok, trinamuzi = divmod(i,3)

    if twnamuzi!=0 and trinamuzi!=0:
        dp[i] = dp[i-1]+1

    elif twnamuzi==0 and trinamuzi!=0:
        dp[i] = min(dp[i-1]+1, dp[twmok]+1)

    elif twnamuzi!=0 and trinamuzi==0:
        dp[i] = min(dp[i-1]+1, dp[trimok]+1)

    else:
        dp[i] = min(dp[i-1]+1 ,dp[twmok]+1, dp[trimok]+1)
    
print(dp[-1])