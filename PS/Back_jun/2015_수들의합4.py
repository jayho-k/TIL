"""
4 0
2 -2 2 -2

"""
# from collections import defaultdict

# n,k = map(int,input().split())
# lst = list(map(int,input().split()))

# dp = [0]
# dp_dic = defaultdict(int)
# dp_dic[0] = 1

# for i in range(n):
#     dp.append(lst[i]+dp[-1])

# ans = 0
# for i in range(1,n+1):

#     if dp[i]-k in dp_dic:
#         ans += dp_dic[dp[i]-k]
#     dp_dic[dp[i]]+=1

# print(ans)

