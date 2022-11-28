'''

4 2
9 7 9 1

1 7 9 9
'''

# tmp = []
# ans = set()
# def dfs(idx,d):
    
#     if d == m:
#         ans.add(tuple(tmp))
#         return
    
#     for i in range(idx,n):
#         tmp.append(lst[i])
#         dfs(i+1,d+1)
#         tmp.pop()

# n,m = map(int,input().split())
# lst = list(map(int,input().split()))
# lst.sort()
# dfs(0,0)

# ans = sorted(list(ans))
# for a in ans:
#     print(*a)





'''
n개 자연수중 m개를 고르는 수열

4 2
9 7 9 1

1 7 9 9
'''

tmp_lst = []
tmp_set = set()
def dfs(d,idx):

    if d == m:
        tmp_set.add(tuple(tmp_lst))
        return

    for i in range(idx,n):
        if not visited[i]:
            tmp_lst.append(lst[i])
            visited[i]=1
            dfs(d+1,i)
            visited[i]=0
            tmp_lst.pop()


n,m = map(int,input().split())
lst = list(map(int,input().split()))
visited=[0]*n
lst.sort()
dfs(0,0)


ans = sorted(list(tmp_set))
for a in ans:
    print(*a)