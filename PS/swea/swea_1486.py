'''

1
5 16
1 3 3 5 6

'''
def dfs(d,s):
    global ans

    if d==n:
        if s>=b:
            ans = min(ans,s)
        return
        
    dfs(d+1,s+tall[d])
    dfs(d+1,s)

for tc in range(1,int(input())+1):
    n,b = map(int,input().split())
    tall = list(map(int,input().split()))
    ans = 1e9
    dfs(0,0)
    print(f"#{tc} {ans-b}")


# from itertools import combinations
# for tc in range(1,int(input())+1):
#     n,b = map(int,input().split())
#     tall = list(map(int,input().split()))
#     mn = 1e9
#     for i in range(1,len(tall)+1):
#         for com_lst in combinations(tall,i):
#             total = 0
#             for com in com_lst:
#                 total+=com
#             if total>=b:
#                 mn = min(total,mn)
#     print(f"#{tc} {mn-b}") 



